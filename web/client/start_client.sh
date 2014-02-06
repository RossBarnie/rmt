#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd $DIR

if [ $# -eq 1 ]; then
    sudo python rmt_client.py $1
else
    echo "Using default configuration, port 8080"
    sudo python rmt_client.py 8080
fi

cd $( pwd )