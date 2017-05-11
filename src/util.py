import os
import random
import string


def substitute_file(from_file, to_file, substitutions):
    """ Substitute contents in from_file with substitutions and
        output to to_file using string.Template class

        Arguments:
        ----------
        from_file -- template file to load
        to_file -- substituted file
        substitutions -- dictionary of substitutions.
    """
    with open(from_file, "r") as f_in:
        source = string.Template(f_in.read())

        with open(to_file, "w") as f_out:
            outcome = source.safe_substitute(substitutions)
            f_out.write(outcome)


def create_scratch_directory(basename):
    """ Creates scratch directory named basename

        Arguments:
        ----------
        basename -- name of folder to create
    """
    if not os.path.isdir(basename):
        os.mkdir(basename)


def only_coordinates(f):
    """ Generator to only consider coordinates in
        xyz-files.

        skips the first two lines
    """
    for i, line in enumerate(f):
        if i > 1:
            yield line

def read_xyz(filename):
    """ Reads an xyz-file """
    with open(filename, "r") as xyz_file:
        for line in only_coordinates(xyz_file):
            data = line.split()
            yield data[0], map(float, data[1:])


def write_xyz(xyz_filename, include_header=True):
    """ Generates an .xyz file output from an .xyz file input """
    xyz_data = list(read_xyz(xyz_filename))
    s = ""
    if include_header:
        s += "{0:d}\n".format(len(xyz_data))
        s += "\n"
    for label, coordinates in xyz_data:
        s += "{0:s}{1[0]:20.9f}{1[1]:16.9f}{1[2]:16.9f}\n".format(label, coordinates)

    return s[:-1]


def directories(from_file):
    """ Sets up directories needed internally in CalcIt.
        This pertains to especially the share directory
        that holds the template files.

        Arguments:
        ----------
        from_file -- the basename to use to extract the files

        Returns:
        --------
        dictionary with paths. The following keys are available:
        path -- the base path for the executable
        bin -- the path for the binary
        share -- the path of the share directory

    """
    abs_path = os.path.abspath(from_file)
    bin_path = os.path.dirname(abs_path)
    path = os.path.dirname(bin_path)
    share_path = os.path.join(path, 'share')
    return {'path': path, 'bin': bin_path, 'share': share_path}


def generate_auth_key(mode):
    """ Generates an authentification key either manually
        or by specifying "auto"

        Arguments:
        ----------
        mode -- the mode used to generate the key.
                auto automatically generates a suitable key.
    """
    key = mode
    if mode == "auto":
        key = "calcit-{0:d}".format(random.randint(10000, 30000))

    return key
