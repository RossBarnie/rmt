#!/bin/bash

if [[ "$UID" -ne 0 ]]
	then echo "please run as root"
	exit 1
else
	exit 0
fi