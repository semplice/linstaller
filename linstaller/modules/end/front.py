# -*- coding: utf-8 -*-
# linstaller end module frontend - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.cli_frontend as cli
import linstaller.core.module as module
import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import warn,info,verbose

class CLIFrontend(cli.CLIFrontend):
	def start(self):
		""" Start the frontend """
		
		self.header(_("Enjoy"))
		
		print(_("Just finished the installation of %(distribution)s.") % {"distribution":self.moduleclass.main_settings["distro"]})
		print(_("Please reboot and remove the install media to get the installed system."))
		print
		
		if not self.settings["reboot"]:
			# We should continue?
			res = self.question(_("Do you want to reboot now?"), default=True)
			if res:
				# Reboot
				return "kthxbye"
			else:
				self.end()
		else:
			# Reboot.
			return "kthxbye"
			

class Module(module.Module):
	def _associate_(self):
		""" Associate frontends. """
		
		self._frontends = {"cli":CLIFrontend}

	def seedpre(self):
		""" Cache configuration used by this module. """
		
		self.cache("reboot")
