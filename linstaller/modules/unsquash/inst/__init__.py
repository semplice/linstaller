# -*- coding: utf-8 -*-
# linstaller unsquash module install - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.module as module
import linstaller.core.libmodules.unsquash.library as lib

class Module(module.Module):
	def start(self):
		""" Start override to unsquash. """

		self.unsquash = lib.Unsquash(self.settings["image"], target=self.main_settings["target"])

		module.Module.start(self)
	
	def revert(self):
		""" Revert mounts """
		
		self.unsquash = lib.Unsquash(self.settings["image"], target=self.main_settings["target"])
		
		try:
			self.unsquash.revert()
		except:
			pass # Try only, if it does not succeed, it is nothing faulty.
		
	def seedpre(self):
		""" Cache preseeds. """
		
		self.cache("image")
