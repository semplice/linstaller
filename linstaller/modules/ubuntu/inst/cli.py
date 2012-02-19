# -*- coding: utf-8 -*-
# linstaller ubuntu module install - (C) 2012 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.frontends.cli as cli
import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import warn,info,verbose

# NOTE: This is a ubuntu-specific module.

class Frontend(cli.Frontend):
	def start(self):
		""" Start the frontend """
				
		# Get a progressbar
		progress = self.progressbar(_("Configuring the final system:"), 2)

		# Start progressbar
		progress.start()
		
		# Copy kernel
		#verbose("Copying kernel...")
		#self.moduleclass.copy_kernel()
		#progress.update(1)

		try:
			# Set kernel and initramfs
			verbose("Configuring kernel...")
			self.moduleclass.install.set_kernel()
			progress.update(1)
			
			# Recompile python modules
			verbose("Recompiling python modules...")
			self.moduleclass.install.configure_python()
			progress.update(2)
		finally:
			# Exit
			self.moduleclass.install.close()
		
		progress.finish()
