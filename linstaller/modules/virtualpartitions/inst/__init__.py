# -*- coding: utf-8 -*-
# linstaller virtualpartitions module install - (C) 2013 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.module as module

from linstaller.core.main import warn,info,verbose
import linstaller.core.libmodules.partdisks.library as lib

import os

class Module(module.Module):
	def _associate_(self):
		""" Shut up associate as we do not have any frontend. """
		
		pass
		
	def start(self):
		""" Do things. """
		
		used = []

		# Bind-mount /dev, /sys and /proc (if no_virtual_partitions is not True):
		if not self.settings["skip"]:
			for point in ("/dev","/sys","/proc"):
				fullpath = os.path.join(self.main_settings["target"],os.path.basename(point))
				if lib.is_mounted(fullpath):
					lib.umount(path=fullpath)
				
				# We can go?
				lib.mount_partition(path=point, opts="bind", target=fullpath, check=False)
				used.append(fullpath)
				
		# Store used
		self.settings["used"] = used
			

	def revert(self):
		""" Umounts virtual partitions, if any. """
		
		# Ensure that we didn't skip
		if not "virtualpartitions.inst" in self.modules_settings or ("skip" in self.modules_settings["virtualpartitions.inst"] and
			self.modules_settings["virtualpartitions.inst"]["skip"]):

			return
			
		# See if "used" was... used :)
		if "used" in self.modules_settings["virtualpartitions.inst"]:
			_used = self.modules_settings["virtualpartitions.inst"]["used"]
			_used.reverse()
			if _used:
				for part in _used:
					if lib.is_mounted(part):
						try:
							lib.umount(path=part, tries=5)
						except:
							pass
	
	def seedpre(self):
		""" Cache settings """
		
		self.cache("skip")
		self.cache("used")
