#!/bin/bash

# Loads linstaller and if something wrong happened, does close window only on ENTER.

linstaller $@
res="$?"

if [ "$res" != "0" ]; then
	# Something wrong happened
	echo
	read -p "Press ENTER to close."
fi

exit $res
