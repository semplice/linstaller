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

import alan.core.extension

import t9n.library as trans

_ = trans.translation_init("linstaller")

# Informations about extension ;)
coders = { "Eugenio Paolantonio":"http://blog.medesimo.eu" }
infos = {"Coders":coders}

class Extension(alan.core.extension.Extension):
	def run(self):
		# Initiate pipemenu
		self.menu = struct.PipeMenu()
		self.menu.start() # add initial tag

		# Get linstaller configuration file, if any
		config = self.cfg.printv("config")
		if not config:
			config = "default"
		persistent_disabled = self.cfg.printv("persistent_disabled")

		config_persistent = self.cfg.printv("config_persistent")
		if not config_persistent:
			config_persistent = "semplice-persistent"
		
		frontend = self.cfg.printv("frontend")
		if not frontend:
			frontend = "glade"

		if frontend == "cli":
			# Proper set executables
			install_ex = "roxterm --hide-menubar -T \"Install Semplice\" -n \"Semplice Live Installer\" -e /usr/bin/linstaller_wrapper.sh -c=%s -f=cli start" % config
			persistent_ex = "roxterm --hide-menubar -T \"Install Semplice in USB\" -n \"Semplice Live USB Installer\" -e /usr/bin/linstaller_wrapper.sh -c=%s -f=cli start" % config_persistent
		else:
			# Default to glade
			install_ex = "sudo /usr/bin/linstaller_crash_wrapper.sh -c=%s -f=glade start" % config
			persistent_ex = "roxterm --hide-menubar -T \"Install Semplice in USB\" -n \"Semplice Live USB Installer\" -e /usr/bin/linstaller_wrapper.sh -c=%s -f=cli start" % config_persistent

		# Alias self.menu.insert() to i()
		i = self.menu.insert

		### Begin!

		install = core.item(_("Start installer"), ga.execute(install_ex))
		
		persistent = core.item(_("Start USB persistent installer"), ga.execute(persistent_ex))

		i(install)
		if not persistent_disabled:
			i(core.separator)
			i(persistent)

		# End
		self.menu.end()

