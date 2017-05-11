#!/usr/bin/env python
# Copyright (C) 2016, Casper Steinmann
#
#
import sys
from distutils.core import setup

# use the source code to get version information
#from src.strings import version_str

__doc__="""CalcIt: a tool to run embarassingly parallel calculations """

# Chosen from http://www.python.org/pypi?:action=list_classifiers
classifiers = """\
Development Status :: 2 - Pre-Alpha
Environment :: Console
Intended Audience :: Science/Research
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Natural Language :: English
Operating System :: OS Independent
Programming Language :: Python
Topic :: Scientific/Engineering :: Chemistry
Topic :: Software Development :: Libraries :: Python Modules
"""

def setup_calcit():
  doclines = __doc__.split("\n")

  setup(name="calcit",
        version="0.1",
        url = "https://github.com/calcit",
        author = "Casper Steinmann",
        author_email = "casper.steinmann@gmail.com",
        maintainer = "Casper Steinmann",
        maintainer_email = "casper.steinmann@gmail.com",
        license = "MIT",
        description = doclines[0],
        long_description = "\n".join(doclines[2:]),      
        classifiers = filter(None, classifiers.split("\n")),
        platforms = ["Any."],
        packages=['calcit'],
        package_dir={'calcit': 'src'},
        scripts=['bin/calcit'],
        data_files=[
                      ('',['README.md','LICENSE']),
                      ('share', [
                                 'share/dalton.bash', 'share/dalton_energy.inp', 'share/dalton_loprop.inp', 'share/dalton_peex.inp',
                                 'share/orca.bash', 'share/orca_energy.inp',
                                 'share/gamess.bash', 'share/gamess_energy.inp',
                                 'share/slave.py', 'share/start_slaves.bash'
                                ])
                   ]
  )

if __name__ == '__main__':
  setup_calcit()
