# -*- coding: utf-8 -*-
# linstaller update module frontend - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

# WARNING: This is a debian-related module!

import linstaller.core.module as module
import t9n.library
_ = t9n.library.translation_init("linstaller")

import apt.cache as cache

from linstaller.core.main import warn,info,verbose

class Install(module.Install):
	def update(self):
		""" Updates the APT cache. """
		
		self.cac = cache.Cache()
		try:
			self.cac.update()
		except:
			verbose("Something went wrong during the cache update.")
	
	def open(self):
		""" Opens the refreshed APT cache. """
		
		self.cac.open()
	
	def check(self):
		""" Checks for updates. """

		pkgs = self.moduleclass.settings["packages"].split(" ")
		
		atleastone = False
		for pkg in pkgs:
			try:
				if self.cac[pkg].is_upgradable:
					info(_("Found version %(version)s of %(package)s.") % {"package":pkg, "version":self.cac[pkg].candidate.version})
					verbose("Marking %s to be upgrated." % pkg)
					self.cac[pkg].mark_upgrade()
					atleastone = True
			except KeyError:
				verbose("Unable to find %s; skipping." % pkg)
		
		if not atleastone:
			return False
		
		return True
	
	def upgrade(self):
		""" Upgrades previously selected packages. """
		
		self.cac.commit()


class Module(module.Module):
	def start(self):
		""" Start module """
		
		self.install = Install(self, onchroot=False)
		
		module.Module.start(self)
	
	def seedpre(self):
		""" Caches variables used by this module. """
		
		self.cache("packages", "linstaller linstaller-modules-base linstaller-frontend-cli")
