# -*- coding: utf-8 -*-
# linstaller unsquash module install - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.module as module
from liblaiv_setup import Language, Keyboard

class Install(module.Install):
	def language(self, language):
		""" Set language. """
		
		self.moduleclass.la.set(language)
	
	def keyboard(self, keyboard, model):
		""" Set keyboard. """
		
		self.moduleclass.ke.set(keyboard, model)

class Module(module.Module):
	def start(self):
		""" Start module. """
		
		self.la = Language()
		self.ke = Keyboard()
		
		self.install = Install(self)
		
		module.Module.start(self)
