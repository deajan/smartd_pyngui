#!/usr/bin/env bash

# Worst travis test script ever !

python smartd_pyngui.py -h
if [ $? == 128 ]; then
	echo "Ok"
else
	exit 1
fi