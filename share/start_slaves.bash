#!/usr/bin/env bash
# this script starts a python multiprocessing slave process
# on a remote node (given as argument to this script) using
# the REMOTE_SHELL protocol.
#
# For your convenience (and debugging satisfaction) it also
# dumps node output and error files (hopefully they are empty!)
$REMOTE_SHELL $1 "if [ -e ~/.bash_profile ]; then source ~/.bash_profile; fi; cd $WORK_DIR; python slave.py >& ${1}.stdout 2> ${1}.stderr  &"
