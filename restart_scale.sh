#!/bin/bash

# Check for pid file
pidfile = ${HOME}/.scaleapp.pid
if [ -f $pidfile ]; then
    # check if process is running
    if ps -p $(cat ${HOME}/.scaleapp.pid) > /dev/null; then
        echo "Scale App is already running"
        exit 1
    fi
    rm -f $pidfile
fi

# activate conda environment
eval "$(conda shell.bash hook)"
conda activate new_scale

# start scale app

export PYTHONPATH=$PYTHONPATH:$HOME/repos

streamlit run scale-scanner-cp.py &

# get PID from background process
pid=$!
echo $pid > $pidfile

