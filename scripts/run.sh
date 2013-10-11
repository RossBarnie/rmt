#!/bin/bash

if [[ "$UID" -ne 0 ]]
	then echo "please run as root"
	exit
fi

python ./start_container.py