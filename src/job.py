import logging
import os

import util

class Job(object):
    """ Job is the base class for all computations in CalcIt

        all jobs has a basename which is based on the .xyz file
        that the user wants to run.

        There are some path-related difficulties when creating jobs that
        needs to be taken care of. For example, if the use has created
        the appropriate directories and are standing (i.e. os.getcwd()) is
        the actual temporary calculation area the Job.cmd command below
        will give the wrong work_dir
    """
    def __init__(self, basename, **kwargs):
        self.basename = basename
        self.work_dir = kwargs.get('work_dir', os.getcwd())
        work_dir = os.path.split(self.work_dir)
        if work_dir[1] == self.basename:
            self.work_dir = work_dir[0]

        self.memory_per_job = kwargs.get('memory_per_job', 512) # in MB
        self.dft_functional = kwargs.get('dft_functional', None)
        self.basis_set = kwargs.get('basis_set', 'sto-3g') # sto-3g per default
        self.cores_per_job = kwargs.get('cores_per_job', 1)
        self.scratch_directory = kwargs.get('scratch_directory', os.environ.get('SCRATCH', ''))

        self.custom_run_script = kwargs.get('custom_run_script', None)

        self.xyz_data = list(util.read_xyz("{0}.xyz".format(basename)))
        self.input_extension = "inp"

    def _setup_default_substitutions(self):
        self._run_script_substitutions = {
          'VERSION': '',
          'PROGPATH': '',
          'NCPUS': self.cores_per_job,
          'JOB': self.get_jobname(),
          'WORK_DIR': os.path.join(self.work_dir, self.basename),
          'SCRATCH': os.path.join(self.scratch_directory, self.get_program(), self.basename),
          'MEMORY': self.get_memory()
        }

        self._comp_chem_substitutions = {
          'NCPUS': self.cores_per_job,
          'MEMORY': self.get_memory(),
          'MP2INFO': '',
          'CHARGE': 0,
          'SCFINFO': self.get_scfinfo(),
          'MULTIPLICITY': 1,
          'BASINFO': self.get_basis_set(),
          'TITLE': self.get_title(),
          'COORDINATE': self.get_coordinates()
        }

    def get_basename(self):
        return self.basename

    def get_jobname(self):
        method = self.get_method()
        basename = self.get_basename()
        return "{0:s}_{1:s}".format(basename, method)

    def get_method(self):
        """ returns <program>_<runtype> """
        program = self.get_program()
        runtype = self.get_runtype()
        return "{0:s}_{1:s}".format(program, runtype)

    def get_program(self):
        if not hasattr(self, 'program'):
            raise NotImplementedError
        return self.program

    def get_runtype(self):
        if not hasattr(self, 'runtype'):
            raise NotImplementedError
        return self.runtype

    def create_scratch_directory(basename):
        if not os.path.isdir(basename):
            os.mkdir(basename)

    def cmd(self, global_paths):
        """ Sets up the command to be run by slave processes. It also
            sets up the correct files needed for a calculation by the
            slave processes.

            NB: Performs some sanity checks

            Arguments:
            ----------
            global_paths -- collection of global paths to use for finding files.
                            NB! They are different from job paths such as the
                            work or scratch directories.

            Returns:
            --------
            The command to run on the slave process.
        """

        # is scratch specified?
        if self.scratch_directory == '':
            raise ValueError("Scratch directory not set. Please specify through SCRATCH enviroment variable.")

        # substitutions for internal variables. First the general and then the program specific.
        self._setup_default_substitutions()
        self._program_substitutions()

        file_to_run = self._setup_files(global_paths['share'])

        s  = "cd {0};".format(os.path.join(self.work_dir, self.basename))
        s += "./{0}".format(file_to_run)
        return s

    def _setup_files(self, share_path):
        program = self.get_program()
        runtype = self.get_runtype()
        basename = self.get_basename()

        self._create_input(share_path)
        file_to_run = self._create_run_script(share_path)

        return file_to_run

    def _create_run_script(self, share_path):
        work_dir = os.getcwd()
        util.create_scratch_directory(self.basename)
        os.chdir(self.basename)

        # always assume that no custom run script is provided
        filename_in = '{0:s}.bash'.format(os.path.join(share_path, self.program))
        if self.custom_run_script is not None:
            filename_in = self.custom_run_script

        filename_out = "{0:s}.sh".format(self.get_jobname())
        xyz_file = '../{0:s}.xyz'.format(self.basename)

        try:
            util.substitute_file(filename_in, filename_out, self._run_script_substitutions)
        except IOError:
            logging.error("Could not substitute from file '{}'. Please check that it exist.".format(os.path.abspath(filename_in)))
            raise util.CalcItJobCreateError("Job: {}".format(str(self)))

        os.chmod(filename_out, 0744)
        os.chdir(work_dir)

        return filename_out

    def _create_input(self, share_path):
        work_dir = os.getcwd()
        util.create_scratch_directory(self.basename)
        os.chdir(self.basename)

        filename_in = '{0:s}.inp'.format(os.path.join(share_path, self.get_method()))
        filename_out = "{0:s}.{1:s}".format(self.get_jobname(), self.input_extension)
        xyz_file = '../{0:s}.xyz'.format(self.basename)

        util.substitute_file(filename_in, filename_out, self._comp_chem_substitutions)

        os.chdir(work_dir)


    def get_title(self):
        return ""


    def _program_substitutions(self):
        """ Load PROGRAM specific substitutions.

            In CalcIt we have two different kinds of substitutions, namely
            SHELL substitutions for the script that runs the QM program
            in the `self._run_script_substitutions` variable and the INPUT
            substitutions in the `self._comp_chem_substitutions` variable

            In general, run script variables are handled through environment
            variables such as QM program location and versions whereas QM
            calculation settings are handled through options specified on
            the command line.

            Environment Variables:
            ----------------------
        """
        raise NotImplementedError


    def get_coordinates(self):
        """ Returns the appropriate coordinates section
            for an input file.

            NB! This should return ONLY the coordinates
                and nothing else
        """
        raise NotImplementedError


    def get_basis_set(self):
        """ Returns the basis set for the program """
        raise NotImplementedError


    def get_memory(self):
        """ Returns a jobs memory requirements

            Programs are free to use whatever unit they see fit
            for example MB, GB or even MWORDS
        """
        raise NotImplementedError

    def get_scfinfo(self):
        """ Returns the SCF method (RHF, DFT) """
        raise NotImplementedError


    def __str__(self):
        raise NotImplementedError("All classes derive from this ")
