# -*- coding: utf-8 -*-
# linstaller core servicehelper library - (C) 2011-12 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.main as main
from linstaller.core.main import info,warn,verbose

def list():
	""" Lists all available modules. Usage: core.servicehelper.list(). """
	
	pass

class Service():
	def __init__(self, servicename):
		""" The module class will represent a module. Just call this class with the module name and then invoke Module.load(). del <module> will unload the module. """
		
		self.servicename = servicename
	
	def load(self, main_settings, service_space, cfg):
		verbose("\nStarting service %s..." % self.servicename)
		# This http://stackoverflow.com/questions/951124/dynamic-loading-of-python-modules/951846#951846 is very helpful! Thanks!
		service = "linstaller.services.%s" % self.servicename
		self.service = __import__(service)
		components = service.split(".")
		for comp in components[1:]:
			self.service = getattr(self.service, comp)
		
		self.mloaded = self.service.Service(main_settings, service_space, cfg)
		return self.mloaded
	
	def __del__(self):
		verbose("Cleaning service object %s..." % self.servicename)
		self.mloaded.close()
		del self.service
