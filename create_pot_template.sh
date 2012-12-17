#!/bin/bash

#
# Simple script that creates an appropriate .pot template into lang/
# Copyright (C) 2011 Eugenio "g7" Paolantonio. All rights reserved.
# Work released under the GNU GPL License, version 3 or later.
#

APP_NAME="linstaller"

find . -name "*.py" | xgettext --language=Python --keyword=_ --output=lang/$APP_NAME/$APP_NAME.pot -f -

# Find and extract from glade files
files=$(find . -name "*.glade")
for glade in $files; do
	if [ `dirname $glade` = "./config" ]; then continue; fi
	intltool-extract --type=gettext/glade $glade
	xgettext --language="C" --keyword=N_ -j --output=lang/$APP_NAME/$APP_NAME.pot -j ${glade}.h
	rm ${glade}.h
done
