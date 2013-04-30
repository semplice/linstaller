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
		self.frontend_settings = moduleclass.main_settings["frontend_settings"]

		self.seedpre()

	def cache(self, var, default=False):
		""" Cache var into self.settings. """
		
		if not var in self.frontend_settings:
			self.frontend_settings[var] = default
	
	def seedpre(self):
		""" Executed to cache seeds. Override this and call self.cache("seed",defaultvar=False) to accomplish this. """
		
		pass

	def module_exit1(self):
		""" Tells the frontend to exit with res == exit1.
		Useful only if you are into a thread. If you aren't into a thread, just use sys.exit.
		"""
		
		# Prevent overwriting the result
		if not self.res == False: return
		
		self.res = "exit1"

	def module_next(self):
		""" Tells the frontend to exit with res == None.
		The frontend must listen to res status. """

		# Prevent overwriting the result
		if not self.res == False: return

		self.on_switching_module()
		self.res = None
	
	def module_prev(self):
		""" Tells the frontend to exit with res == back.
		The frontend must listen to res status. """

		# Prevent overwriting the result
		if not self.res == False: return

		self.on_switching_module()
		self.res = "back"
			
	def module_reboot(self):
		""" Tells the frontend to exit with res == KTHXBYE.
		The frontend must listen to res status. """

		# Prevent overwriting the result
		if not self.res == False: return

		self.on_switching_module()
		self.res = "kthxbye"

	def module_restart(self):
		""" Tells the frontend to exit with res == restart.
		The frontend must listen to res status. """

		# Prevent overwriting the result
		if not self.res == False: return

		self.on_switching_module()
		self.res = "restart"

	def module_fullrestart(self):
		""" Tells the frontend to exit with res == fullrestart.
		The frontend must listen to res status. """

		# Prevent overwriting the result
		if not self.res == False: return

		self.on_switching_module()
		self.res = "fullrestart"
	
	def module_casper(self):
		""" Tells the frontend to exit with res == casper.
		The frontend must listen to res status. """

		# Prevent overwriting the result
		if not self.res == False: return

		self.on_switching_module()
		self.res = "casper"
	
	def end(self):
		""" close frontend and parents. """
		
		main.verbose("User requested to end.")
		sys.exit(0)

	def on_switching_module(self):
		""" Called when switching module. """
		
		pass
