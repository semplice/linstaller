#!/bin/bash
#
# Mount an iso image/cdrom in order to use the nolive capabilities of linstaller.
# Copyright (C) 2011 Eugenio "g7" Paolantonio. All rights reserved.
# Work released under the terms of the GNU GPL license, version 3 or later.
#

error() {
	echo "E: $@" >&2
	exit 1
}

case "$1" in
	-h|--help)
		cat <<EOF
$0 -- mount an iso image/cdrom in order to use the nolive capabilites of linstaller.

USAGE: $0 <iso_image>

If <iso_image> is omitted, the cdrom drive will be used.
EOF
;;
	"")
		DEVICE="/dev/sr0";;
	*)
		DEVICE="$1";;
esac

[ "$UID" != 0 ] && error "You need to be root to use $0!"

echo "Creating required directories..."
[ ! -e "/linstaller/source" ] && mkdir -p "/linstaller/source"

echo "Checking device..."
[ ! -e "$DEVICE"  ] && error "$DEVICE does not exist."

echo "Mounting image..."
mount "$DEVICE" /linstaller/source || error "An error occoured while mounting the device (is it empty?)"

echo
echo
echo "The image is now mounted. You can run linstaller with the nolive configuration file to install the distribution."
echo "If you're about to install semplice, the configuration file is \"semplice-nolive\"."
echo "Have fun!"

exit
