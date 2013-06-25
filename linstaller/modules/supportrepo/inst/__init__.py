# -*- coding: utf-8 -*-
# linstaller supportrepo module install - (C) 2013 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.module as module
import linstaller.core.aptlib as aptl

import os

class Module(module.Module):
	def _associate_(self):
		""" Shut up associate as we do not have any frontend. """
		
		pass
	
	def start(self):
		""" Start module. """
		
		# When installing a 32-bit system from a 64-bit one, APT will
		# not like that the target is foreign, and will default to amd64.
		# We clearly do not want this, as we can install only 'all' packages.
		# To workaround this issue, we need to force the architecture in
		# target's APT configuration.
		# We need to get the target arch and as we can't rely on the kernel
		# one and we are outside chroot (damn!) we can only use the
		# /etc/semplice64-build and /etc/semplice-build.
		# The mayor drawback is that custom distributions will have the
		# architecture not forced, but as it's unlikely to install
		# a 32-bit system from a 64-bit one (unless one is a linstaller developer)
		# we can go ahead.
		
		with open(os.path.join(self.main_settings["target"], "etc/apt/apt.conf.d/100linstaller"), "w") as f:
			if os.path.exists(os.path.join(self.main_settings["target"], "etc/semplice64-build")):
				# We are 64!
				f.write("APT::Architecture \"amd64\";")
			elif os.path.exists(os.path.join(self.main_settings["target"], "etc/semplice-build")):
				# We are 32!
				f.write("APT::Architecture \"i386\";")
		
		# If none of above, linstaller will continue to work as usual,
		# just ensure that is running from the same live system as the
		# target, as it's in the 99.9% of the cases.
		
		# We need to support older semplice-current releases (Semplice 4)
		# which may get this linstaller by auto-update and will not be
		# able to install the bootloader because it will try to install
		# the packages from the CD (repositories have been added starting
		# from Semplice 5)
				
		if os.path.exists(self.settings["path"].replace("file://","").replace("http://","").replace("https://","").replace("ftp://","")):
			self.cache = aptl.Cache(rootdir=self.main_settings["target"])
			self.cache.add_repository(aptl.RepositoryType.TRIVIAL, self.settings["path"], binarydir=self.settings["binarydir"])
			
			# Update
			self.cache.update()
			self.cache.open()
						
			# Cache the cache object. This will be used by whoever wants to use the supportrepo.
			self.settings["cache"] = self.cache
		else:
			self.settings["cache"] = None
	
	def revert(self):
		""" Revert changes. """
		
		# Remove the forced architecture
		path = os.path.join(self.main_settings["target"], "etc/apt/apt.conf.d/100linstaller")
		if os.path.exists(path):
			os.remove(path)
	
	def seedpre(self):
		""" Cache settings """
		
		self.cache("path")
		self.cache("binarydir", "./")
