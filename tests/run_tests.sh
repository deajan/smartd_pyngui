#!/usr/bin/env bash

# Worst travis test script ever !

BASE_DIR="$(pwd)"
BASE_DIR="${BASE_DIR%%/tests*}"

find "$BASE_DIR" -name "*.pyc" -or -name "__pycache__" | xargs -I {} rm -rf {}

export PYTHONPATH=$BASE_DIR

cd "$BASE_DIR" || (echo "Cannot switch to directory [$BASE_DIR]." && exit 1)

python smartd_pyngui/smartd_pyngui.py -h
if [ $? == 128 ]; then
	echo "App launched from shell okay."
else
	echo "Cannot launch app from shell."
	exit 1
fi

py.test
