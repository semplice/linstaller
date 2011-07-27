# -*- coding: utf-8 -*-
# linstaller bootloader module frontend - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.cli_frontend as cli
import linstaller.core.main as m
import linstaller.core.module as module
import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import warn,info,verbose

class CLIFrontend(cli.CLIFrontend):
	def start(self):
		""" Start the frontend """
		
		self.header(_("Bootloader"))
		
		if not self.settings["bootloader"]:
			# Should ask.
			
			print(_("The bootloader is that piece of software that lets you boot your %(distroname)s system.") % {"distroname":self.moduleclass.main_settings["distro"]})
			print(_("Without the bootloader, you can't boot %(distroname)s.") % {"distroname":self.moduleclass.main_settings["distro"]})
			print
			print(_("You can choose to install the bootloader into the Master Boot Record of your hard disk. This is recommended."))
			print(_("If you choose 'No', it will be installed on your root partition.") + "\n")
			
			result = self.question(_("Do you want to install the bootloader into the MBR?"), default=True)
			if result:
				# Yay
				self.settings["bootloader"] = "mbr"
			else:
				# Root
				self.settings["bootloader"] = "root"
		
		verbose("Bootloader will be installed in %s" % self.settings["bootloader"])

class Module(module.Module):
	def _associate_(self):
		""" Associate frontends. """
		
		self._frontends = {"cli":CLIFrontend}
	
	def seedpre(self):
		""" Caches variables used by this module. """
		
		self.cache("bootloader")
