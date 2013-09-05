#!/bin/bash

# Loads linstaller and if something wrong happened, displays the crash dialog.

sudo linstaller "$@"
res="$?"

if [ "$res" != "0" ]; then
	# Something wrong happened
	python /usr/share/linstaller/crash/crash_window.py
fi

## FIXME: This should be handled by stock linstaller, but sometimes target
## remains mounted and we clearly do not want it
sudo umount /linstaller/target/{proc,dev,sys,boot/efi,} &> /dev/null

exit $res
