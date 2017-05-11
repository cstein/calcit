# CalcIt
CalcIt runs files embarrasingly parallel.

## Getting Started
CalcIt comes preloaded with the nescessary scripts to run Orca and GAMESS.
To run those programs, calcit needs to know where they are located.
Please see the **setting up programs** section just below.
Once the correct environment variables have been set, an Orca energy calculation on all .xyz files in the current folder can be executed as

    calcit *.xyz --program=orca

### Setting up Programs
#### DALTON
To properly locate DALTON you must provide **one** environment variable.
The `DALTON` environment variable points to the directory where DALTON is installed.

    export DALTON=/path/to/where/dalton/is/installed

If you have not installed DALTON yourself you should talk to your system administrator to get this information.
#### GAMESS
To properly locate GAMESS you must provide **two** environment variables.
Both `GAMESS` and `GAMVER` which are, respectively, the path to the GAMESS installation and the version number.

    export GAMESS=/path/to/where/gamess/is/installed
    export GAMVER=00

Here we have specified that CalcIt should use version 00 of GAMESS.
If you have not compiled GAMESS yourself you should talk to your system administrator to get this information.

#### Orca
To properly locate Orca you must provide **one** environment variable.
The `ORCA` environment variable points to the directory where Orca is installed.

    export ORCA=/path/to/where/orca/is/installed

If you have not installed Orca yourself you should talk to your system administrator to get this information.

### Usage notes
Upon execution, CalcIt uses `ssh` to launch slave processes on all available nodes through an auto generated script called `start_slaves.sh`.
This script sources your `~/.bash_profile` in order to give you a chance to set up your paths correctly (look elsewhere in this README for instructions on how to do that)
It is important that CalcIt is in the python path (`PYTHONPATH` environment variable) when executing, otherwise the program will hang.

## Extending CalcIt
It is quite straightforward to extend CalcIt with either your own program or by extending it to allow for a different runtype.
