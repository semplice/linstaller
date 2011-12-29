# -*- coding: utf-8 -*-
# linstaller language module frontend - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.module as module
from liblaiv_setup import Language, Keyboard

class Module(module.Module):
	def start(self):
		""" Start module. """
		
		self.la = Language()
		self.ke = Keyboard()
		
		module.Module.start(self)
	
	def seedpre(self):
		""" Caches variables used by this module. """
		
		self.cache("ask")
		self.cache("language")
		self.cache("keyboard")
		
		## INTERNAL
		self.cache("_model")
