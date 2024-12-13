#!/bin/bash

# HOME=custom home dir if needed

WATCH=$HOME/watchfolder/dir1
TARGET=$HOME/watchfolder/dir2
export LOGDIR=$HOME'/logs'

python3 $HOME/crontest/crontest/crontest.py $WATCH $TARGET
