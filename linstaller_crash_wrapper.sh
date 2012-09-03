#!/bin/bash

# Loads linstaller and if something wrong happened, displays the crash dialog.

sudo linstaller $@
res="$?"

if [ "$res" != "0" ]; then
	# Something wrong happened
	/usr/share/linstaller/crash/crash_window.py
fi

exit $res
