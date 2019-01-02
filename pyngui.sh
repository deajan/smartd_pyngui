#!/usr/bin/env sh

if type python3 > /dev/null 2>&1; then
	python3 ./smartd_pyngui/smartd_pyngui.py
else
	python ./smartd_pynggui/smartd_pyngui.py
fi
