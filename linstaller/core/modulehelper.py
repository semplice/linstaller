# -*- coding: utf-8 -*-
# linstaller core modulehelper library - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.main as main
from linstaller.core.main import info,warn,verbose

def list():
	""" Lists all available modules. Usage: core.modulehelper.list(). """
	
	pass

class Module():
	def __init__(self, modulename):
		""" The module class will represent a module. Just call this class with the module name and then invoke Module.load(). del <module> will unload the module. """
		
		self.modulename = modulename
	
	def load(self, main_settings, modules_settings, service_started, cfg):
		verbose("\nLoading module %s..." % self.modulename)
		# This http://stackoverflow.com/questions/951124/dynamic-loading-of-python-modules/951846#951846 is very helpful! Thanks!
		module = "linstaller.modules.%s" % self.modulename
		self.module = __import__(module)
		components = module.split(".")
		for comp in components[1:]:
			self.module = getattr(self.module, comp)
		
		self.mloaded = self.module.Module(main_settings, modules_settings, service_started, cfg, module)
		return self.mloaded
	
	def __del__(self):
		verbose("Unloading module %s..." % self.modulename)
		del self.module
