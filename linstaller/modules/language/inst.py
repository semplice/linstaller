# -*- coding: utf-8 -*-
# linstaller unsquash module install - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.cli_frontend as cli
import linstaller.core.module as module
import linstaller.core.main as m
import t9n.library
_ = t9n.library.translation_init("linstaller")

import linstaller.core.libmodules.chroot.library as lib

from linstaller.core.main import warn,info,verbose

from liblaiv_setup import Language, Keyboard
la = Language()
ke = Keyboard()

class CLIFrontend(cli.CLIFrontend):
	def start(self):
		""" Start the frontend """

		# Get a progressbar
		progress = self.progressbar(_("Setting Language & Keyboard:"), 2)
		
		verbose("Setting language and keyboard")
		
		# Enter in target
		chroot = lib.Chroot()
		chroot.open()
		
		# Get.
		language = self.moduleclass.modules_settings["language"]["language"]
		keyboard = self.moduleclass.modules_settings["language"]["keyboard"]
		model = self.moduleclass.modules_settings["language"]["_model"]
				
		# Start progressbar
		progress.start()
		
		try:
			# Set language
			la.set(language)
			progress.update(1)
			
			# Set keyboard and model
			ke.set(keyboard, model)
			progress.update(2)
		finally:
			# Exit from chroot
			chroot.close()		
		
		progress.finish()
		
		verbose("Done.")

class Module(module.Module):
	def _associate_(self):
		""" Associate frontends. """
		
		self._frontends = {"cli":CLIFrontend}
