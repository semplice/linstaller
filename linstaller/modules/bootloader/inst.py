# -*- coding: utf-8 -*-
# linstaller bootloader module install - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.cli_frontend as cli
import linstaller.core.module as module
import linstaller.core.main as m
import commands
import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import warn,info,verbose
import linstaller.core.libmodules.chroot.library as lib

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

class CLIFrontend(cli.CLIFrontend):
	def start(self):
		""" Start the frontend """

		_install = {"grub":self.moduleclass.install.grub_install}
		_update = {"grub":self.moduleclass.install.grub_update}

		# Get bootloader
		bootloader = self.moduleclass.modules_settings["bootloader"]["bootloader"]

		verbose("Installing %s bootloader..." % bootloader)
		
		# Get a progressbar
		progress = self.progressbar(_("Installing bootloader:"), 2)

		# Start progressbar
		progress.start()

		# PASS 1: INSTALL
		_install[bootloader]()
		progress.update(1)
		
		# PASS 2: UPDATE
		_update[bootloader]()
		progress.update(2)

		# Exit
		self.moduleclass.install.close()
		
		progress.finish()

class Module(module.Module):
	def start(self):
		""" Start module """
		
		self.install = Install(self)
		
		module.Module.start(self)
		
	def _associate_(self):
		""" Associate frontends. """
		
		self._frontends = {"cli":CLIFrontend}
