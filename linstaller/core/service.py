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
		
		self.is_ready = False
		
		self.main_settings = main_settings
		self.service_space = service_space
		self.cfg = cfg
		
		self.running = True
		
		self.current_module = None
		self.current_frontend = None
		
		self.ready()
		self.is_ready = True
		
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
	
	def kthxbye(self, obj=None):
		""" Tells the module to reboot. """
		
		self.current_module.module_reboot()
	
	def fullrestart(self, obj=None):
		""" Tells the module to do fullrestart. """
		
		self.current_module.module_fullrestart()
	
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
	
	def do_caspered(self, status):
		""" Executed when a casper status has been done. """
		
		self.on_caspered(status)
	
	def on_caspered(self, status):
		""" Override this to do things when caspered is triggered. """
		
		pass
