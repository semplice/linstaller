# -*- coding: utf-8 -*-
# linstaller language module install - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.module as module
from keeptalking import Locale, Keyboard

class Install(module.Install):
	def language(self, locale):
		""" Set language. """
		
		self.moduleclass.la.set(locale)
	
	def savespace(self, locale):
		""" Set savespace. """
		
		self.moduleclass.la.savespace_enable(locale)
	
	def purge(self, locale):
		""" Purges superflous locales. """
		
		self.moduleclass.la.savespace_purge(locale)
	
	def keyboard(self, layout=None, model=None, variant=None):
		""" Set keyboard. """
		
		self.moduleclass.ke.set(layout=layout, model=model, variant=variant)

class Module(module.Module):
	def start(self):
		""" Start module. """
		
		self.la = Locale.Locale()
		self.ke = Keyboard.Keyboard()
		
		self.install = Install(self)
		
		module.Module.start(self)
