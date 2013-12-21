# -*- coding: utf-8 -*-
#
# Alan: Semplice Menu Extension Framework
# Copyright (C) 2011-2013 Eugenio "g7" Paolantonio and the Semplice Team.
# Work released under the terms of the GNU GPL License, version 3 or later.
#
# This file cointain the laiv_installer extension

import alan.core.extension as extension
from alan.core.objects.separator import Separator
from alan.core.objects.item import Item
from alan.core.objects.actions import ExecuteAction

import t9n.library as trans

_ = trans.translation_init("linstaller")

class Extension(extension.Extension):
	
	extensionName = "linstaller"
	
	def generate(self):

		# Get linstaller configuration file, if any
		if "config" in self.extension_settings:
			config = self.extension_settings["config"]
		else:
			config = "default"
		
		if "persistent_disabled" in self.extension_settings:
			persistent_disabled = self.extension_settings["persistent_disabled"]
		else:
			persistent_disabled = False

		if "config_persistent" in self.extension_settings:
			config_persistent = self.extension_settings["config_persistent"]
		else:
			config_persistent = "semplice-persistent"
		
		if "frontend" in self.extension_settings:
			frontend = self.extension_settings["frontend"]
		else:
			frontend = "glade"

		if frontend == "cli":
			# Proper set executables
			install_ex = "roxterm --hide-menubar -T \"Install Semplice\" -n \"Semplice Live Installer\" -e /usr/bin/linstaller_wrapper.sh -c=%s -f=cli start" % config
			persistent_ex = "roxterm --hide-menubar -T \"Install Semplice in USB\" -n \"Semplice Live USB Installer\" -e /usr/bin/linstaller_wrapper.sh -c=%s -f=cli start" % config_persistent
		else:
			# Default to glade
			install_ex = "sudo /usr/bin/linstaller_crash_wrapper.sh -c=%s -f=glade start" % config
			persistent_ex = "roxterm --hide-menubar -T \"Install Semplice in USB\" -n \"Semplice Live USB Installer\" -e /usr/bin/linstaller_wrapper.sh -c=%s -f=cli start" % config_persistent

		# Alias self.add() to i()
		i = self.add

		### Begin!

		install = self.return_executable_item(_("Start installer"), install_ex)
		
		persistent = self.return_executable_item(_("Start USB persistent installer"), persistent_ex)

		i(install)
		if not persistent_disabled:
			i(Separator())
			i(persistent)

	def return_executable_item(self, label, command):
		""" Returns an executable item. """
				
		item = Item(label=label)
		action = ExecuteAction(command)
		item.append(action)
		
		return item


