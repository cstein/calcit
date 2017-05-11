#!/usr/bin/env bash
# runs an ORCA calculation
#
# options to be substituted
#  WORK_DIR: $WORK_DIR
#  SCRACTH : $SCRATCH
#  PATH    : $PROGPATH
#  JOB     : $JOB
#

if [ ! -e $WORK_DIR/$JOB.out ]
then

    mkdir -p $SCRATCH
    cp $JOB.inp $SCRATCH
    cd $SCRATCH
    
    # run the calculation
    $PROGPATH/orca $JOB.inp > $WORK_DIR/$JOB.out
    
    cd $WORK_DIR
    rm -rf $SCRATCH
else
    echo "Skipping $JOB because output exists."
fi
