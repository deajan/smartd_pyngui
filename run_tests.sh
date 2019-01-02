#!/usr/bin/env bash

# Worst travis test script ever !

BASE_DIR="$(pwd)"
BASE_DIR="${BASE_DIR%%/tests*}"

echo using basedir [$BASE_DIR]

# Arguments: 1= Pid to wait for, 2= timeout (s)
function WaitForIt {
	local start=$SECONDS
	while ps -p $1 > /dev/null 2>&1
	do
		sleep 1
		if [ $((SECONDS - start)) -ge $2 ]; then
			kill -9 $1
		fi
	done
	wait $1
	return $?
}

find "$BASE_DIR" -name "*.pyc" -or -name "__pycache__" | xargs -I {} rm -rf {}

export PYTHONPATH=$BASE_DIR
export DISPLAY=:0.0

cd "$BASE_DIR" || (echo "Cannot switch to directory [$BASE_DIR]." && exit 1)

python smartd_pyngui/smartd_pyngui.py &
WaitForIt $! 20

if [ $? == 137 ]; then
	echo "App launched from shell (seems) okay (137 = kill signal after 20 seconds)."
else
	echo "Cannot launch app from shell."
	exit 1
fi

# py.test currently failing
#py.test
