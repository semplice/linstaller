# -*- coding: utf-8 -*-
# linstaller semplice module install - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
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

# NOTE: This is a semplice-specific module.

class Install(module.Install):

	def livemode(self):
		""" Removes /etc/semplice-live-mode. """
		
		if os.path.exists("/etc/semplice-live-mode"):
			os.remove("/etc/semplice-live-mode")

class Module(module.Module):
	def start(self):
		""" Start module """
		
		self.install = Install(self)
		try:
			self.install.livemode()
		finally:
			self.install.close()
