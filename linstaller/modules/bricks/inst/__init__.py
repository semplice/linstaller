# -*- coding: utf-8 -*-
# linstaller bricks module install - (C) 2013 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.module as module

import bricks.engine as engine

class Install(module.Install):
	def run(self, InstallProgress):

		atleastone = False

		for feature, choice in self.moduleclass.modules_settings["bricks"]["features"].items():
			
			status, packages, allpackages = engine.status(feature)
			
			if not choice:
				# remove!
				atleastone = True
				engine.remove(packages)
		
		# Commit
		if atleastone:
			engine.cache.commit(install_progress=InstallProgress)

class Module(module.Module):
	def start(self):
		""" Start module. """
		
		self.install = Install(self)
		
		module.Module.start(self)
