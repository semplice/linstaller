# -*- coding: utf-8 -*-
# linstaller virtualclean module install - (C) 2012 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.frontends.cli as cli
import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import warn,info,verbose

class Frontend(cli.Frontend):
	def start(self):
		""" Start the frontend """

		verbose("Removing virtual machine specific packages...")
		
		# Get a progressbar
		progress = self.progressbar(_("Removing virtual machine specific packages:"), 1)

		# Start progressbar
		progress.start()

		try:
			# Type
			typ = self.moduleclass.install.type
			
			# Remove
			self.moduleclass.install.remove(typ)
			progress.update(1)
		finally:
			# Exit
			self.moduleclass.install.close()
		
		progress.finish()
