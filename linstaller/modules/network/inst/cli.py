# -*- coding: utf-8 -*-
# linstaller network module install - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.frontends.cli as cli
import linstaller.core.main as m
import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import warn,info,verbose

class Frontend(cli.Frontend):
	def start(self):
		""" Start the frontend """

		verbose("Configuring networking...")
		
		# Get a progressbar
		progress = self.progressbar(_("Configuring networking:"), 1)

		# Start progressbar
		progress.start()

		verbose("Configuring networking")
		try:
			# NETWORKING: set.
			self.moduleclass.install.configure()
			progress.update(1)
		finally:
			# Exit
			self.moduleclass.install.close()
		
		progress.finish()

