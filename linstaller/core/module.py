# -*- coding: utf-8 -*-
# linstaller core module sample class module - (C) 2010 Eugenio "g7" Paolantonio and the µSoft Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.main as main
import linstaller.core.libmodules.chroot.library as chlib

class Install:
	""" Executed during install. """
	
	def __init__(self, moduleclass, onchroot=True):
		""" Sets moduleclass to self.moduleclass """
		
		self.moduleclass = moduleclass
		self.onchroot = onchroot
		
		if self.onchroot:
			# Enter in chroot
			self.ch = chlib.Chroot()
			self.ch.open()

	def close(self):
		""" Return to normal root. """
		
		if self.onchroot:
			self.ch.close()	

class Module:
	def __init__(self, main_settings, modules_settings, cfg, package):
		""" This init function will take the args and submodule passed to the module. """
		
		self.main_settings, self.modules_settings, self.cfg, self.package = main_settings, modules_settings, cfg, package
		
		self.settings = {}
		self.changed = {} # Convienent dict to store changed items. Useful mainly for partdisks.
		
		self.seedpre()
		self.preseed()

		# Associate
		self._associate_()

	def _associate_(self):
		""" Get appropriate frontend. """
				
		# Frontend discovery
		frontend = "%s.%s" % (self.package, self.main_settings["frontend"])
		loaded = __import__(frontend)
		components = frontend.split(".")
		for comp in components[1:]:
			loaded = getattr(loaded, comp)
						
		self._frontends = {self.main_settings["frontend"]:loaded.Frontend}

	def start(self):
		""" Start the module. """
		
		# Initiate the relevant frontend class.
		frnt = self._frontends[self.main_settings["frontend"]](self)
		
		# Start frnt.
		res = frnt.start()
		
		if res in ("restart", "kthxbye", "fullrestart","back"):
			return res
	
	def seedpre(self):
		pass
	
	def cache(self, var, default=False):
		""" Cache var into self.settings. """
		
		self.settings[var] = default
	
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
