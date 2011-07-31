# -*- coding: utf-8 -*-
# linstaller core module sample class module - (C) 2010 Eugenio "g7" Paolantonio and the µSoft Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.main as main
import linstaller.core.libmodules.chroot.library as chlib

class Install:
	""" Executed during install. """
	
	def __init__(self, moduleclass):
		""" Sets moduleclass to self.moduleclass """
		
		self.moduleclass = moduleclass
		
		# Enter in chroot
		self.ch = chlib.Chroot()
		self.ch.open()

	def close(self):
		""" Return to normal root. """
		
		self.ch.close()	

class Module:
	def __init__(self, main_settings, modules_settings, cfg):
		""" This init function will take the args and submodule passed to the module. """
		
		self.main_settings, self.modules_settings, self.cfg = main_settings, modules_settings, cfg
		
		self.settings = {}
		self.changed = {} # Convienent dict to store changed items. Useful mainly for partdisks.
		
		self.seedpre()
		self.preseed()

	def start(self):
		""" Start the module. """
		
		# Associate
		self._associate_()
		
		# Initiate the relevant frontend class.
		frnt = self._frontends[self.main_settings["frontend"]](self)
		
		# Start frnt.
		res = frnt.start()
		
		if res == "restart":
			# Frontend requested to restart
			return "restart"
	
	def seedpre(self):
		pass
	
	def cache(self, var):
		""" Cache var into self.settings. """
		
		self.settings[var] = False
	
	def preseed(self):
		""" looks for preseeded items into configuration. """
		
		cfg = self.cfg
		if cfg.has_section(cfg.module):
			options = cfg.config.options(cfg.module)
			for opt in options:
				# Insert in self.settings
				self.settings[opt] = cfg.printv(opt)

	def return_settings(self):
		""" Returns modules's settings. """
		
		return self.settings
