# -*- coding: utf-8 -*-
# linstaller bootloader module install - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.module as module
import linstaller.core.main as m

from linstaller.core.main import warn,info,verbose

class Install(module.Install):
	def grub_install(self):
		""" Installs grub. """

		# Get target
		target = self.moduleclass.modules_settings["bootloader"]["device"]

		verbose("Selected location: %s" % target)

		if target == "root":
			# Root.
			location = self.moduleclass.modules_settings["partdisks"]["root"]
			args = "--no-floppy --force"
		else:
			# MBR
			location = "(hd0)"
			args = "--no-floppy"
			
		m.sexec("grub-install %(args)s '%(location)s'" % {"args":args,"location":location})
	
	def grub_update(self):
		""" Updates grub menu list """

		m.sexec("update-grub")

class Module(module.Module):
	def start(self):
		""" Start module """
		
		self.install = Install(self)
		self._install = {"grub":self.install.grub_install}
		self._update = {"grub":self.install.grub_update}
		
		module.Module.start(self)

