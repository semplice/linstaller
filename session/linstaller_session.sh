#!/bin/bash
#
# linstaller session - (C) 2013 Eugenio "g7" Paolantonio.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#

if [ "$1" ]; then
	CONFIG="/etc/linstaller/$1"
else
	CONFIG="/etc/linstaller/default"
fi

# If default, read the link and see if there is a -fullscreen configuration (e.g. semplice-fullscreen):
if [ "$CONFIG" == "/etc/linstaller/default" ]; then
	LNK="`readlink $CONFIG`"
	[ -e "$LNK-fullscreen" ] && CONFIG="$LNK-fullscreen"
fi

if [ "$2" == "__internal" ]; then
	/usr/bin/linstaller_crash_wrapper.sh -f=glade -c=`basename $CONFIG` start
	sudo reboot
	exit
else
	# Launch openbox and linstaller
	exec /usr/bin/openbox --startup "/usr/bin/linstaller_session.sh `basename $CONFIG` __internal"
fi
