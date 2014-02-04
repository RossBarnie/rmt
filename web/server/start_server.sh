#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd $DIR

python rmt_server.py 192.168.0.3:1234

cd $( pwd )
