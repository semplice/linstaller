# -*- coding: utf-8 -*-
# linstaller unsquash module install - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.module as module
from liblaiv_setup import TimeZone

class Install(module.Install):
	def set(self, timezone):
		""" Sets timezone. """
		
		self.moduleclass.tz.set(timezone)

class Module(module.Module):
	def start(self):
		""" Start module. """
		
		self.tz = TimeZone()
		self.install = Install(self)

		module.Module.start(self)
