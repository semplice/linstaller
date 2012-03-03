# -*- coding: utf-8 -*-
# linstaller echo.copy module install - (C) 2012 Eugenio "g7" Paolantonio and the Semplice Team.
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
		progress = self.progressbar(_("Copying system to disk:"), 2)

		# Start progressbar
		progress.start()

		# Copy squashfs image...
		verbose("Copying squashfs image...")
		self.moduleclass.copy()

		# Update
		progress.update(1)
		
		# Copy syslinux directory...
		verbose("Copying syslinux directory...")
		self.moduleclass.copy_syslinux()

		# Update
		progress.update(2)

		# Close progressbar
		progress.finish()
