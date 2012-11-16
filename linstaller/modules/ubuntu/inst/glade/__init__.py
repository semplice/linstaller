# -*- coding: utf-8 -*-
# linstaller ubuntu module install - (C) 2012 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.frontends.glade as glade
import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import warn,info,verbose

# NOTE: This is a ubuntu-specific module.

class Configure(glade.Progress):
	def progress(self):
		""" Do things. """
		
		self.parent.progress_wait_for_quota()
		
		try:
			# Set kernel and initramfs
			self.parent.progress_set_text(_("Configuring kernel..."))
			self.parent.moduleclass.install.set_kernel()
			self.parent.progress_set_percentage(1)
			
			# Recompile python modules
			self.parent.progress_set_text(_("Recompiling python modules..."))
			self.parent.moduleclass.install.configure_python()
			self.parent.progress_set_percentage(2)
		finally:
			# Exit
			self.parent.moduleclass.install.close()

class Frontend(glade.Frontend):
	def ready(self):
		""" Start the frontend """

		self.set_header("hold", _("Configuring the final system..."), "")

		self.progress_set_quota(2)
	
	def process(self):
		
		clss = Configure(self)
		clss.start()
