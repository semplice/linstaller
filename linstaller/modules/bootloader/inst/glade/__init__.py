# -*- coding: utf-8 -*-
# linstaller bootloader module install - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.main as m
import linstaller.frontends.glade as glade
import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import warn,info,verbose

class BootloaderInstall(glade.Progress):
	def progress(self):
		
		self.parent.progress_wait_for_quota()
		
		# Should we skip?
		if self.parent.moduleclass.modules_settings["bootloader"]["skip"]:
			return

		# Get bootloader
		bootloader = self.parent.moduleclass.modules_settings["bootloader"]["bootloader"]

		m.verbose("Installing %s bootloader..." % bootloader)
		
		# PASS 1: FETCHING THE ARCHIVES
		self.parent.progress_set_text(_("Fetching bootloader packages..."))
		self.parent.moduleclass._pkgs_fetch[bootloader]()
		self.parent.progress_set_percentage(1)

		# Now, enter into the chroot...
		self.parent.moduleclass.install_phase()
		
		try:
			# PASS 2: INSTALLING THE PACKAGES
			self.parent.progress_set_text(_("Installing bootloader packages..."))
			self.parent.moduleclass._pkgs_install[bootloader]()
			self.parent.progress_set_percentage(2)
			
			# PASS 3: INSTALL
			self.parent.progress_set_text(_("Installing bootloader..."))
			self.parent.moduleclass._install[bootloader]()
			self.parent.progress_set_percentage(3)
			
			# PASS 4: UPDATE
			self.parent.progress_set_text(_("Generating bootloader configuration..."))
			self.parent.moduleclass._update[bootloader]()
			self.parent.progress_set_percentage(4)
		finally:
			# Exit
			self.parent.moduleclass.install.close()


class Frontend(glade.Frontend):
	def ready(self):
		""" Start the frontend """
		
		self.set_header("hold", _("Installing bootloader..."), _("Please wait during the installer is installing the bootloader..."))
		
		self.progress_set_quota(4)
	
	def process(self):
		""" Process install """
		
		clss = BootloaderInstall(self)
		clss.start()
