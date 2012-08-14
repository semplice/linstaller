# -*- coding: utf-8 -*-
# linstaller core frontend sample class module - (C) 2012 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import sys

import linstaller.core.main as main

class Frontend:
	def __init__(self, moduleclass):
		
		self.res = False
		
		self.moduleclass = moduleclass
		self.settings = moduleclass.settings
		self.changed = moduleclass.changed

	def module_next(self):
		""" Tells the frontend to exit with res == None.
		The frontend must listen to res status. """
		
		self.on_switching_module()
		self.res = None
	
	def module_prev(self):
		""" Tells the frontend to exit with res == back.
		The frontend must listen to res status. """
				
		self.on_switching_module()
		self.res = "back"
			
	def module_reboot(self):
		""" Tells the frontend to exit with res == KTHXBYE.
		The frontend must listen to res status. """
		
		self.on_switching_module()
		self.res = "kthxbye"
	
	def module_fullrestart(self):
		""" Tells the frontend to exit with res == fullrestart.
		The frontend must listen to res status. """
		
		self.on_switching_module()
		self.res = "fullrestart"
	
	def module_casper(self):
		""" Tells the frontend to exit with res == casper.
		The frontend must listen to res status. """
		
		self.on_switching_module()
		self.res = "casper"
	
	def end(self):
		""" close frontend and parents. """
		
		main.verbose("User requested to end.")
		sys.exit(0)

	def on_switching_module(self):
		""" Called when switching module. """
		
		pass
