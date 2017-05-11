import os

from .job import Job

class GAMESSJob(Job):
    """ Base class for all GAMESS calculations

        Subclasses are responsible for setting the correct parameters
        in the calculation.
    """
    def __init__(self, basename, **kwargs):
        Job.__init__(self, basename, **kwargs)
        self.program = 'gamess'

    def get_coordinates(self):
        """ Returns the appropriate coordinates section
            for an input file.

            NB! This should return ONLY the coordinates
                and nothing else
        """
        Z = {'H': 1, 'C': 6, 'N': 7, 'O': 8, 'S': 16}
        s = ""
        for label, coordinates in self.xyz_data:
            s += "{0:s}{1:2d}{2[0]:20.9f}{2[1]:16.9f}{2[2]:16.9f}\n".format(label, Z[label], coordinates)

        return s[:-1]

    def _program_substitutions(self):
        """ Load GAMESS specific substitutions.

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
            GAMESS -- location of the GAMESS executables
            GAMVER -- the GAMESS version to use
        """

        # first we do run_script substitutions
        path = os.environ.get('GAMESS')
        if path is None:
            raise ValueError("GAMESS environment variable not set to path of GAMESS installation.")

        version = os.environ.get('GAMVER')
        if version is None:
            raise ValueError("GAMVER environment variable not set to proper GAMESS version.")

        self._run_script_substitutions['VERSION'] = version
        self._run_script_substitutions['PROGPATH'] = path

        # then input substitutions. We provide RHF as the default
        self._comp_chem_substitutions['SCFINFO'] = "SCFTYP=RHF"
        self._comp_chem_substitutions['MP2INFO'] = "MPLEVL=0"

    def get_memory(self):
        """ GAMESS wants memory in good old mega words """
        return int(self.memory_per_job * 1024 * 1024 / 8e6)

    def get_basis_set(self):
        """ Returns the basis set for the GAMESS

            Implemented as a non-exhaustive lookup table
        """
        gamess_basis_sets = {
            'sto-3g': "$BASIS GBASIS=STO NGAUSS=3 $END",
            '3-21G': "$BASIS GBASIS=N21 NGAUSS=3 $END",
            '6-31G': "$BASIS GBASIS=N31 NGAUSS=6 $END",
            '6-31G*': "$BASIS GBASIS=N31 NGAUSS=6 NDFUNC=1 $END",
            '6-31G(d)': "$BASIS GBASIS=N31 NGAUSS=6 NDFUNC=1 $END",
            '6-31+G*': "$BASIS GBASIS=N31 NGAUSS=6 NDFUNC=1 DIFFSP=.T. $END",
            '6-31+G(d)': "$BASIS GBASIS=N31 NGAUSS=6 NDFUNC=1 DIFFSP=.T. $END",
            'cc-pVDZ': "$BASIS GBASIS=CCD $END",
            'cc-pVTZ': "$BASIS GBASIS=CCT $END",
            'aug-cc-pVDZ': "$BASIS GBASIS=ACCD $END",
            'aug-cc-pVTZ': "$BASIS GBASIS=ACCT $END"
        }

        if not gamess_basis_sets.has_key(self.basis_set):
            raise ValueError("GAMESS does not recognize the '{0:s}' basis set. Please report this to the author.".format(self.basis_set))

        return gamess_basis_sets[self.basis_set]


class GAMESSEnergyJob(GAMESSJob):
    def __init__(self, basename, **kwargs):
        GAMESSJob.__init__(self, basename, **kwargs)
        self.runtype = 'energy'

    def substitutions(self):
        pass

    def __str__(self):
        return "GAMESS Energy ({0:s})".format(self.basename)

    def __repr__(self):
        return "GAMESSEnergyJob('{0:s}')".format(self.basename)
