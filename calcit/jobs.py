from .gamess import GAMESSEnergyJob
from .orca import OrcaEnergyJob
from .dalton import DALTONEnergyJob

program_matrix = {
    'energy': {'gamess': GAMESSEnergyJob, 'orca': OrcaEnergyJob, 'dalton': DALTONEnergyJob}
    }

def EnergyJob(basename, program=None, **kwargs):
    """ Convenience wrapper for energy calculation classes.

        Arguments:
        ----------
        basename -- base name (no extension) of the molecule to calculate
        program -- The quantum chemistry program to run
        kwargs -- keyword based arguments
    """
    if program is None:
        raise ValueError("Program not supplied as argument 2 to EnergyJob.")

    matrix = program_matrix['energy']
    matrix_keys = matrix.keys()
    if program not in matrix.keys():
        raise ValueError("Program '{0:s}' not supported. Please use one of {1:s}".format(program, matrix_keys))

    return matrix[program](basename, **kwargs)

