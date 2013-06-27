# -*- coding: utf-8 -*-
# linstaller bootloader module install - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
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

		# Get bootloader
		bootloader = self.moduleclass.modules_settings["bootloader"]["bootloader"]

		verbose("Installing %s bootloader..." % bootloader)
		
		# Get a progressbar
		progress = self.progressbar(_("Installing bootloader:"), 4)

		# Start progressbar
		progress.start()
		
		# PASS 1: FETCHING THE ARCHIVES
		self.moduleclass._pkgs_fetch[bootloader]()
		progress.update(1)
		
		# Now, enter into the chroot...
		self.moduleclass.install_phase()

		try:
			# PASS 2: INSTALLING THE PACKAGES
			self.moduleclass._pkgs_install[bootloader]()
			progress.update(2)
					
			# PASS 3: INSTALL
			self.moduleclass._install[bootloader]()
			progress.update(3)
			
			# PASS 4: UPDATE
			self.moduleclass._update[bootloader]()
			progress.update(4)
		finally:
			# Exit
			self.moduleclass.install.close()
		
		progress.finish()
