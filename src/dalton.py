import os

from .job import Job

class DALTONJob(Job):
    """ Base class for all DALTON calculations

        Subclasses are responsible for setting the correct parameters
        in the calculation.
    """
    def __init__(self, basename, **kwargs):
        Job.__init__(self, basename, **kwargs)
        self.program = 'dalton'
        self.input_extension = 'dal'

    def get_coordinates(self):
        xyz_data = self.xyz_data
        Z = {'H': 1, 'C': 6, 'N': 7, 'O': 8, 'S': 16}

        # DALTON groups coordinates with the same nuclear charge.
        # we first loop over coordinates to get information we
        # need to later make the correcting printing.

        # for each group we need their nuclear charge which is
        # what differentiates them
        n_atom_types = 0
        group_nuclear_charge= -1
        groupcounts = []
        groupcharges = []
        for elem, coord in xyz_data:
            if group_nuclear_charge != Z[elem]:
                 group_nuclear_charge= Z[elem]
                 n_atom_types += 1
                 groupcounts.append(0)
                 groupcharges.append(group_nuclear_charge)

            # store the number of atoms in the group
            groupcounts[n_atom_types-1] += 1

        # We force that no molecule shall be treated (or attempted) to be
        # treated with symmetry.
        s = "AtomTypes={0:d} Angstrom NoSymmetry\n".format(n_atom_types)

        # now print atoms
        n_atom_types = 0
        group_nuclear_charge= -1
        for elem, coord in xyz_data:
            if group_nuclear_charge != Z[elem]:
                 group_nuclear_charge= Z[elem]
                 n_atom_types += 1
                 s += "Charge={0:d} Atoms={1:d}\n".format(group_nuclear_charge, groupcounts[n_atom_types-1])

            s += "{0:<3s} {1[0]:22.10f} {1[1]:14.10f} {1[2]:14.10f}\n".format(elem, coord)
        return s


    def _program_substitutions(self):
        """ Load DALTON specific substitutions.

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
            DALTON -- path to DALTON installation
        """

        # first we do run_script substitutions
        path = os.environ.get('DALTON')
        if path is None:
            raise ValueError("DALTON environment variable not set to path of DALTON installation.")

        self._run_script_substitutions['PROGPATH'] = path

        # then input substitutions
        self._comp_chem_substitutions['SCFINFO'] = ".HF"

    def get_memory(self):
        return self.memory_per_job

    def get_basis_set(self):
        return self.basis_set

    def get_title(self):
        """ Dalton uses TWO lines for the title """
        return "\n"

class DALTONEnergyJob(DALTONJob):
    def __init__(self, basename, **kwargs):
        DALTONJob.__init__(self, basename, **kwargs)
        self.runtype = 'energy'

    def substitutions(self):
        pass

    def __str__(self):
        return "DALTON Energy ({0:s})".format(self.basename)

    def __repr__(self):
        return "DALTONEnergyJob('{0:s}')".format(self.basename)

    
