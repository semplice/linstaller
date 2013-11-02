# -*- coding: utf-8 -*-
# linstaller core modulehelper library - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import importlib

import linstaller.core.main as main
from linstaller.core.main import info,warn,verbose

class Module():
	def __init__(self, modulename):
		""" The module class will represent a module. Just call this class with the module name and then invoke Module.load(). del <module> will unload the module. """
		
		self.modulename = modulename
	
	def load(self, main_settings, modules_settings, service_started, cfg):
		verbose("\nLoading module %s..." % self.modulename)
		
		module = "linstaller.modules.%s" % self.modulename
		self.module = importlib.import_module(module)
		
		self.mloaded = self.module.Module(main_settings, modules_settings, service_started, cfg, module)
		return self.mloaded
	
	def __del__(self):
		verbose("Unloading module %s..." % self.modulename)
		del self.module
