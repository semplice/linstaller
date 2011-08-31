#!/bin/bash

#
# Simple script that creates an appropriate .pot template into lang/
# Copyright (C) 2011 Eugenio "g7" Paolantonio. All rights reserved.
# Work released under the GNU GPL License, version 3 or later.
#

APP_NAME="linstaller"

find . -name "*.py" | xgettext --language=Python --keyword=_ --output=lang/$APP_NAME/$APP_NAME.pot -f -
