#!/usr/bin/env python
from distutils.core import setup

from src.strings import version_str

__author__ = "Casper Steinmann"
__copyright__ = "Copyright (C) 2017"
__license__ = 'MIT'
__version__ = version_str
__email__ = "casper.steinmann@gmail.com"
__url__ = "https://github.com/FragIt/fragit-main"
__doc__="""CalcIt: a tool to run embarassingly parallel calculations """

def setup_calcit():
  doclines = __doc__.split("\n")

  setup(name="calcit",
        version=__version__,
        url = __url__,
        author = __author__,
        author_email = __email__,
        maintainer = __author__,
        maintainer_email = __email__,
        license = __license__,
        description = doclines[0],
        long_description = "\n".join(doclines[2:]),      
        platforms = "Any",
        packages=['calcit'],
        package_dir={'calcit': 'src'},
        scripts=['bin/calcit'],
        data_files=[
                      ('',['README.md','LICENSE']),
                      ('share', [
                                 'share/dalton.bash', 'share/dalton_energy.inp',
                                 'share/dalton_loprop.inp', 'share/dalton_peex.inp',
                                 'share/dalton_pde_monomer.inp', 'share/dalton_pde_dimer.inp',
                                 'share/orca.bash', 'share/orca_energy.inp',
                                 'share/gamess.bash', 'share/gamess_energy.inp',
                                 'share/slave.py', 'share/start_slaves.bash'
                                ])
                   ]
  )

if __name__ == '__main__':
  setup_calcit()
