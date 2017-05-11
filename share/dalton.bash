#!/usr/bin/env bash
# runs a DALTON calculation
#
# options to be substituted
#  WORK_DIR: $WORK_DIR
#  SCRACTH : $SCRATCH
#  PATH    : $PROGPATH
#  JOB     : $JOB
#  MEMORY  : $MEMORY
#

if [ ! -e $WORK_DIR/$JOB.out ]
then

    export DALTON_TMPDIR=$SCRATCH
    export DALTON_NUM_MPI_PROCS=$NCPUS
    export OMP_NUM_THREADS=1
    
    # run the calculation
    $PROGPATH/dalton -mb $MEMORY -noappend -ow $JOB.dal

else
    echo "Skipping $JOB because output exists."
fi
