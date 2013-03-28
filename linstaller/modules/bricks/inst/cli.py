# -*- coding: utf-8 -*-
# linstaller bricks module install - (C) 2013 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.frontends.cli as cli
import linstaller.core.main as m
import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import warn,info,verbose

import apt.progress.base

class InstallProgress(apt.progress.base.InstallProgress):
	""" Handles the Install step. """
	
	def __init__(self, progress):
		
		apt.progress.base.InstallProgress.__init__(self)
		
		self.progress = progress
	
	def status_change(self, pkg, percent, status):
		""" Update percentage. """
				
		apt.progress.base.InstallProgress.status_change(self, pkg, percent, status)
		
		self.progress.update(int(percent))
		
		return True

class Frontend(cli.Frontend):
	def start(self):
		""" Start the frontend """

		# Get a progressbar
		progress = self.progressbar(_("Configuring features:"), 100)
		
		verbose("Configuring features")

		# Start progressbar
		progress.start()

		try:
			self.moduleclass.install.run(InstallProgress(progress))
		finally:
			# Exit
			self.moduleclass.install.close()
		
		progress.finish()
		
