# -*- coding: utf-8 -*-
# linstaller timezone module install - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.frontends.glade as glade
import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import warn,info,verbose

class Set(glade.Progress):
	def progress(self):
		""" Do things. """
		
		self.parent.progress_wait_for_quota()

		# Get.
		timezone = self.parent.moduleclass.modules_settings["timezone"]["timezone"]

		try:
			self.parent.progress_set_text(_("Setting timezone..."))
			self.parent.moduleclass.install.set(timezone)
			self.parent.progress_set_percentage(1)
		finally:
			# Exit
			self.parent.moduleclass.install.close()


class Frontend(glade.Frontend):
	def ready(self):
		""" Start the frontend """

		verbose("Setting timezone")
		self.set_header("hold", _("Setting timezone..."), _("This may take a while."))
		
		self.progress_set_quota(1)
	
	def process(self):
		
		clss = Set(self)
		clss.start()
