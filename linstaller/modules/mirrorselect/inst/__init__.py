# -*- coding: utf-8 -*-
# linstaller mirrorselect module install - (C) 2012 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.module as module
import os
import linstaller.core.main as m

from linstaller.core.main import info,warn,verbose

class Install(module.Install):
	def prechecks(self):
		""" Checks if mirrorselect exists and a working internet connection is present. """
		
		if not os.path.exists("/usr/bin/mirrorselect"):
			verbose("mirrorselect is not installed.")
			return False
		
		try:
			m.sexec("ping -c1 www.google.com")
		except:
			# No connection
			verbose("A working internet connection is not present.")
			return False
		
		return True
	
	def select(self, set):
		""" Selects the fastest mirror using mirrorselect. """
		
		verbose("Running mirrorselect with set %s..." % set)
		
		# Create arguments
		args = []
		args.append("-s %s" % set) # Set
		args.append("-n") # Non-interactive
		if self.moduleclass.modules_settings["mirrorselect"]["enable_sources"]: args.append("-o") # Enable sources
		
		m.sexec("/usr/bin/mirrorselect %s" % " ".join(args))

class Module(module.Module):
	def start(self):
		""" Start module. """
		
		self.install = Install(self)
		
		module.Module.start(self)
