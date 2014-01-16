# -*- coding: utf-8 -*-
# linstaller core changelocale library - (C) 2014 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import locale

def change(newlocale):
	locale.setlocale(locale.LC_ALL, newlocale)
