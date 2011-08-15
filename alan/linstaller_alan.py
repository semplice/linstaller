# -*- coding: utf-8 -*-
#
# Alan: Semplice Menu Extension Framework
# Copyright (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# Work released under the terms of the GNU GPL License, version 3 or later.
#
# This file cointain the laiv_installer extension

import alan.core.structure as struct
import alan.core.objects.core as core
import alan.core.actions.glob as ga

import t9n.library as trans

_ = trans.translation_init("linstaller")

# Informations about extension ;)
coders = { "Eugenio Paolantonio":"http://blog.medesimo.eu" }
infos = {"Coders":coders}

# Initiate pipemenu
menu = struct.PipeMenu()
menu.start() # add initial tag

# Alias menu.insert() to i()
i = menu.insert

### Begin!

install = core.item(_("Go Classic!"), ga.execute("roxterm --hide-menubar -T \"Install Semplice\" -n \"Semplice Live Installer\" -e /usr/bin/linstaller_wrapper.sh -c=default start"))

i(install)

# End
menu.end()

