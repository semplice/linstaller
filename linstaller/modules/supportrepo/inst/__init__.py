# -*- coding: utf-8 -*-
# linstaller supportrepo module install - (C) 2013 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.module as module
import linstaller.core.apt as aptl

import os

class Module(module.Module):
	def _associate_(self):
		""" Shut up associate as we do not have any frontend. """
		
		pass
	
	def start(self):
		""" Start module. """
		
		# We need to support older semplice-current releases (Semplice 4)
		# which may get this linstaller by auto-update and will not be
		# able to install the bootloader because it will try to install
		# the packages from the CD (repositories have been added starting
		# from Semplice 5)
		
		if os.path.exists(self.settings["path"])
			self.cache = aptl.Cache(rootdir=self.main_settings["target"])
			self.cache.add_repository(aptl.RepositoryType.TRIVIAL, self.settings["path"], binarydir=self.settings["binarydir"])
			
			# Update
			self.cache.update()
			
			# Cache the cache object. This will be used by whoever wants to use the supportrepo.
			self.settings["cache"] = self.cache
		else:
			self.settings["cache"] = None
	
	def revert(self):
		""" Revert changes. """
		
		# Is this really needed? (cache created with memonly and sources file in /tmp)
		pass
	
	def seedpre(self):
		""" Cache settings """
		
		self.cache("path")
		self.cache("binarydir", "./")
