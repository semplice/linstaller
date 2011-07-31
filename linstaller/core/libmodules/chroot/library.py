# -*- coding: utf-8 -*-
# chroot library. - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.main as m
import operator
import os
import time

from linstaller.core.main import info,warn,verbose

# Kudos to http://www.sarathlakshman.com/2010/08/12/exit-from-chroot-environment-python/ !!!

class Chroot:
	def __init__(self, target=False):
		""" Main function of Chroot class. """
		
		if not target:
			self.target = "/linstaller/target"
		else:
			self.target = target
	
	def open(self):
		""" Enters into the chroot. """
		
		self.current = os.path.abspath(".")
		self.real = os.open("/", os.O_RDONLY)
		
		# CHROOT IT!!!!!!!!!111111111111!!!!!!!!!!111111111111
		os.chroot(self.target)
		os.chdir("/")
	
	def close(self):
		""" Exits from the chroot. """
		
		os.fchdir(self.real)
		os.chroot(".")
		
		# Close, finally
		os.close(self.real)
		
		# Enter in self.current
		os.chdir(self.current)
