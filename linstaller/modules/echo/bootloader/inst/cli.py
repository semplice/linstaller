# -*- coding: utf-8 -*-
# linstaller echo.partusb module install - (C) 2012 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.frontends.cli as cli
import t9n.library
_ = t9n.library.translation_init("linstaller")

class Frontend(cli.Frontend):
	def start(self):
		""" Start the frontend """
		
		# Get a progressbar
		progress = self.progressbar(_("Installing bootloader:"), 1)

		# Start progressbar
		progress.start()

		# PASS 1: INSTALL
		self.moduleclass.install()
		progress.update(1)
		
		progress.finish()
