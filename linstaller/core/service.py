# -*- coding: utf-8 -*-
# linstaller core service sample class module - (C) 2012 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.main as main
import linstaller.core.libmodules.chroot.library as chlib

import threading

class Service(threading.Thread):
	def __init__(self, main_settings, service_space, cfg):
		""" Welcome to linstaller services! """
		
		self.main_settings = main_settings
		self.service_space = service_space
		self.cfg = cfg
		
		self.running = True
		
		self.current_module = None
		self.current_frontend = None
		
		self.ready()
		
		threading.Thread.__init__(self)
	
	def ready(self):
		""" Override this to execute things when the Service object is created. """
		
		pass
	
	def run(self):
		""" This needs to be filled if the service needs to stay on the background doing things.
		It is not required. """
		
		pass
	
	def close(self):
		""" This *TELLS* the service to close. But it actually does not close it at all. """
		
		#main.verbose("Closing service...")
		self.running = False
		self.on_close()
	
	def next_module(self):
		""" Tells the module to close everything and to let linstaller import the next one. """
		
		self.current_module.module_next()
	
	def prev_module(self):
		""" Tells the module to close everything and let linstaller import the previous one. """
		
		self.current_module.module_prev()
	
	def on_close(self):
		""" Executed when the user closes the service. """
		
		pass
	
	def do_module_change(self, module):
		""" This changes the current module. """
		
		self.current_module =  module
		self.on_module_change()
	
	def on_module_change(self):
		""" Executed when the module is changed. """
		
		pass
	
	def do_frontend_change(self, frontend):
		""" This changes the current frontend. """
		
		self.current_frontend = frontend
		self.on_frontend_change()
	
	def on_frontend_change(self):
		""" Executed when the frontend is changed. """
		
		pass

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
