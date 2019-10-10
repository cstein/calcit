import os

from .job import Job

class OrcaJob(Job):
    """ Base class for all ORCA calculations

        Subclasses are responsible for setting the correct parameters
        in the calculation.
    """
    def __init__(self, basename, **kwargs):
        Job.__init__(self, basename, **kwargs)
        self.program = 'orca'

    def get_coordinates(self):
        """ Returns the appropriate coordinates section
            for an input file.

            NB! This should return ONLY the coordinates
                and nothing else
        """
        s = ""
        for label, coordinates in self.xyz_data:
            s += "{0:s}{1[0]:20.9f}{1[1]:16.9f}{1[2]:16.9f}\n".format(label, coordinates)
        return s[:-1]

    def get_memory(self):
        """ Orca wants memory in MB """
        return self.memory_per_job

    def get_basis_set(self):
        """ Returns the basis set for the ORCA """
        return self.basis_set.upper()

    def _program_substitutions(self):
        """ Load ORCA specific substitutions.

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
            ORCA -- path to orca installation
        """

        path = os.environ.get('ORCA')
        if path is None:
            raise ValueError("ORCA environment variable not set to path of Orca installation.")

        # first we do run_script substitutions
        self._run_script_substitutions['PROGPATH'] = path

        # then input substitutions
        self._comp_chem_substitutions['SCFINFO'] = "HF"


class OrcaEnergyJob(OrcaJob):
    def __init__(self, basename, **kwargs):
        OrcaJob.__init__(self, basename, **kwargs)
        self.runtype = 'energy'

    def __str__(self):
        return "Orca Energy ({0:s})".format(self.basename)

    def __repr__(self):
        return "OrcaEnergyJob('{0:s}')".format(self.basename)
