#!/usr/bin/env bash
# runs a GAMESS calculation
#
# TODO: GAMESS has it's own SCRATCH management which
#       most likely will break with this setup
#
# options:
#  PATH    : $PROGPATH
#  JOB     : $JOB
#  VERSION : $VERSION
#  SCRATCH : $SCRATCH
#  # CPUS  : $NCPUS
#

#
# the GAMESS rungms script was modified to make it understand
# the TMPDIR env variable outside of the PBS path in order
# to customize scratch space.
#
if [ ! -e $JOB.out ]
then
    mkdir -p $SCRATCH
    export TMPDIR=$SCRATCH
    $PROGPATH/rungms $JOB.inp $VERSION $NCPUS > $JOB.out
    rm -rf $SCRATCH
else
    echo "Skipping $JOB because output exists."
fi
