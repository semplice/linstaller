# -*- coding: utf-8 -*-
# linstaller echo.partusb module install - (C) 2012 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.frontends.cli as cli
import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import verbose

class Frontend(cli.Frontend):
	def start(self):
		""" Start the frontend """
		
		# Get a progressbar
		progress = self.progressbar(_("Creating persistent filesystem:"), 3)

		# Start progressbar
		progress.start()

		# Create persistent filesystem...
		verbose("Creating persistent filesystem...")
		self.moduleclass.create()

		# Update
		progress.update(1)
		
		# Format filesystem...
		verbose("Formatting filesystem...")
		self.moduleclass.format()

		# Update
		progress.update(2)
		
		# Configure filesystem...
		verbose("Configuring filesystem...")
		self.moduleclass.configure()
		
		# Update
		progress.update(3)

		# Close progressbar
		progress.finish()
