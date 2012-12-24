#!/bin/bash

# Loads linstaller and if something wrong happened, does close window only on ENTER.

sudo linstaller "$@"
res="$?"

if [ "$res" != "0" ]; then
	# Something wrong happened
	echo
	read -p "Press ENTER to close."
fi

## FIXME: This should be handled by stock linstaller, but sometimes target
## remains mounted and we clearly do not want it
sudo umount /linstaller/target/{proc,dev,sys,} &> /dev/null

exit $res
