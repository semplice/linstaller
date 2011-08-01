# -*- coding: utf-8 -*-
# linstaller debian module install - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
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

# NOTE: This is a debian-specific module.

class Install(module.Install):

	## NOTE: You should specify a file that lists all packages to be removed into the configuration file ('remove')

	def get(self):
		""" Gets the number of the packages to be removed. """
		
		return len(self.moduleclass.packages)
		
	def remove(self, pkg):
		""" Removes pkg. """
		
		m.sexec("apt-get remove --yes --force-yes --purge %s -o DPkg::NoTriggers=true" % pkg)

class CLIFrontend(cli.CLIFrontend):
	def start(self):
		""" Start the frontend """

		verbose("Removing live-specific packages...")
		
		# Get a progressbar
		progress = self.progressbar(_("Removing live-specific packages:"), self.moduleclass.install.get())

		# Start progressbar
		progress.start()

		try:
			num = 0
			for pkg in self.moduleclass.packages:
				num += 1
				verbose("  Removing %s" % pkg)
				
				# Remove package
				self.moduleclass.install.remove(pkg)
				progress.update(num)
		finally:
			# Exit
			self.moduleclass.install.close()
		
		progress.finish()

class Module(module.Module):
	def start(self):
		""" Start module """

		# Cache packages list as we will later enter chroot...
		self.packages = []
		with open(self.settings["remove"], "r") as f:
			_lines = f.readlines()
			for line in _lines:
				self.packages.append(line.replace("\n",""))
		
		self.install = Install(self)
		
		module.Module.start(self)
		
	def _associate_(self):
		""" Associate frontends. """
		
		self._frontends = {"cli":CLIFrontend}
	
	def seedpre(self):
		""" Cache configuration """
		
		self.cache("remove")
