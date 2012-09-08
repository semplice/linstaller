# -*- coding: utf-8 -*-
# linstaller echo.copy module install - (C) 2012 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.frontends.glade as glade
import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import warn,info,verbose


class Copy(glade.Progress):
	def progress(self):
		""" Do things. """
		
		self.parent.progress_wait_for_quota()
		
		# Create persistent filesystem...
		self.parent.progress_set_text(_("Copying squashfs image..."))
		self.parent.moduleclass.copy()
		self.parent.progress_set_percentage(1)
		
		# Format filesystem...
		self.parent.progress_set_text(_("Copying syslinux directory..."))
		self.parent.moduleclass.copy_syslinux()
		self.parent.progress_set_percentage(2)


class Frontend(glade.Frontend):
	def ready(self):
		""" Start the frontend """
		
		# Get a progressbar
		self.set_header("hold", _("Copying system to disk..."), _("This may take a while."))

		self.progress_set_quota(2)
	
	def process(self):
		
		clss = Copy(self)
		clss.start()
