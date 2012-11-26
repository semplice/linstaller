# -*- coding: utf-8 -*-
# linstaller echo.partusb module install - (C) 2012 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.frontends.glade as glade
import t9n.library
_ = t9n.library.translation_init("linstaller")
	
from linstaller.core.main import warn,info,verbose


class Create(glade.Progress):
	def progress(self):
		""" Do things. """
		
		self.parent.progress_wait_for_quota()
		
		# Create persistent filesystem...
		self.parent.progress_set_text(_("Creating persistent filesystem..."))
		self.parent.moduleclass.create()
		self.parent.progress_set_percentage(1)
		
		# Format filesystem...
		self.parent.progress_set_text(_("Formatting filesystem..."))
		self.parent.moduleclass.format()
		self.parent.progress_set_percentage(2)
		
		# Configure filesystem...
		self.parent.progress_set_text(_("Configuring filesystem..."))
		self.parent.moduleclass.configure()
		self.parent.progress_set_percentage(3)


class Frontend(glade.Frontend):
	def ready(self):
		""" Start the frontend """
		
		# Get a progressbar
		self.set_header("hold", _("Creating persistent filesystem..."), _("This may take a while."))

		self.progress_set_quota(3)
	
	def process(self):
		
		clss = Create(self)
		clss.start()
