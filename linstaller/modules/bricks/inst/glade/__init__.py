# -*- coding: utf-8 -*-
# linstaller bricks module install - (C) 2013 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.frontends.glade as glade
import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import warn,info,verbose

import apt.progress.base

class InstallProgress(apt.progress.base.InstallProgress):
	""" Handles the Install step. """
	
	def __init__(self, parent):
		
		apt.progress.base.InstallProgress.__init__(self)
		
		self.parent = parent
	
	def status_change(self, pkg, percent, status):
		""" Update percentage. """
				
		self.parent.progress_set_text(status + "...")
		
		apt.progress.base.InstallProgress.status_change(self, pkg, percent, status)
		
		self.parent.progress_set_percentage(percent)
		
		return True

class Configure(glade.Progress):
	def progress(self):
		""" Do things. """
		
		self.parent.progress_wait_for_quota()

		try:
			self.parent.moduleclass.install.run(InstallProgress(self.parent))
		finally:
			# Exit
			self.parent.moduleclass.install.close()


class Frontend(glade.Frontend):
	def ready(self):
		""" Start the frontend """

		verbose("Configuring features")
		self.set_header("hold", _("Configuring features..."), _("This may take a while."))
		
		self.progress_set_quota(100)
	
	def process(self):
		
		clss = Configure(self)
		clss.start()
