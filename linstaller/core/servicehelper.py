# -*- coding: utf-8 -*-
# linstaller core servicehelper library - (C) 2011-14 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import importlib

import linstaller.core.main as main
from linstaller.core.main import info,warn,verbose

class Service():
	def __init__(self, servicename):
		""" The service class will represent a service. Just call this class with the service name and then invoke Service.load(). del <service> will unload the service. """
		
		self.servicename = servicename
	
	def load(self, main_settings, service_space, cfg):
		verbose("\nStarting service %s..." % self.servicename)
		
		service = "linstaller.services.%s" % self.servicename
		self.service = importlib.import_module(service)
		
		self.mloaded = self.service.Service(main_settings, service_space, cfg)
		return self.mloaded
	
	def __del__(self):
		verbose("Cleaning service object %s..." % self.servicename)
		self.mloaded.close()
		del self.service
