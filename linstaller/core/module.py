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
			self.ch = chlib.Chroot(target=self.moduleclass.main_settings["target"])
			self.ch.open()

	def close(self):
		""" Return to normal root. """
		
		if self.onchroot:
			self.ch.close()	

class Module:
	def __init__(self, main_settings, modules_settings, service_started, cfg, package):
		""" This init function will take the args and submodule passed to the module. """
		
		self.main_settings, self.modules_settings, self.cfg, self.service_started, self.package = main_settings, modules_settings, cfg, service_started, package
		
		self.settings = {"caspered":False}
		self.changed = {} # Convienent dict to store changed items. Useful mainly for partdisks.
		
		self.seed_setup()
		
		self.seedpre()
		self.preseed()

		# Add settings from a previous execution, if any
		pkg = package.replace("linstaller.modules.","").replace(".front","")
		if pkg in self.modules_settings:
			for item, key in self.modules_settings[pkg].items():
				self.settings[item] = key

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
		self.frnt = self._frontends[self.main_settings["frontend"]](self)
		
		# Trigger the frontend change
		for service, obj in self.service_started.items():
			obj.do_frontend_change(self.frnt)
		
		# Start frnt.
		res = self.frnt.start()
		
		if res in ("restart", "exit1", "kthxbye", "fullrestart","back","casper"):
			return res
	
	def module_exit1(self):
		""" Tells the frontend to force exit installation with status 1 """
		
		try:
			self.front.module_exit1()
		except:
			pass
	
	def module_next(self):
		""" Tells the frontend to close the module (thus let linstaller go on the next one) """
		
		try:
			self.frnt.module_next()
		except:
			pass
	
	def module_prev(self):
		""" Tells the frontend to close the module with "back" result. """
		
		try:
			self.frnt.module_prev()
		except:
			pass
	
	def module_reboot(self):
		""" Tells the frontend to close the module with "KTHXBYE" result. """
		
		try:
			self.frnt.module_reboot()
		except:
			pass

	def module_restart(self):
		""" Tells the frontend to close the module with "restart" result. """
		
		try:
			self.frnt.module_restart()
		except:
			pass

	def module_fullrestart(self):
		""" Tells the frontend to close the module with "fullrestart" result. """
		
		try:
			self.frnt.module_fullrestart()
		except:
			pass
	
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

	def seed_setup(self):
		""" Override this to execute things before the seeding occours.
		
		Mainly useful to change cfg.module to a foreign module. """
		
		pass

	def return_settings(self):
		""" Returns modules's settings. """
		
		# This may raise an exception if frontend-less module... handle accordingly
		try:
			return self.frnt.settings
		except:
			return self.settings
