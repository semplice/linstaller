# -*- coding: utf-8 -*-
# linstaller clean module install - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.cli_frontend as cli
import linstaller.core.module as module
import linstaller.core.main as m
import commands
import shutil
import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import warn,info,verbose
import linstaller.core.libmodules.chroot.library as lib

class Install(module.Install):
	def removeconfiguration(self):
		""" Removes linstaller-related configuration files.
		
		This should be executed *after* the package removing process."""
		
		if os.path.exists("/etc/linstaller/"):
			shutil.rmtree("/etc/linstaller/")

class CLIFrontend(cli.CLIFrontend):
	def start(self):
		""" Start the frontend """

		verbose("Cleaning...")
		
		# Get a progressbar
		progress = self.progressbar(_("Cleaning:"), 1)

		# Start progressbar
		progress.start()

		verbose("Removing linstaller-related configuration files...")
		try:
			# NETWORKING: set.
			self.moduleclass.install.removeconfiguration()
			progress.update(1)
		finally:
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
