# -*- coding: utf-8 -*-
# linstaller clean module install - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.module as module
import os, shutil

class Install(module.Install):
	def removeconfiguration(self):
		""" Removes linstaller-related configuration files.
		
		This should be executed *after* the package removing process."""
		
		if os.path.exists("/etc/linstaller/"):
			shutil.rmtree("/etc/linstaller/")

class Module(module.Module):
	def start(self):
		""" Start module """
		
		self.install = Install(self)
		
		module.Module.start(self)
