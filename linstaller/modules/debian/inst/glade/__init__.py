# -*- coding: utf-8 -*-
# linstaller debian module install - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.frontends.glade as glade
import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import warn,info,verbose

# NOTE: This is a debian-specific module.

class Remove(glade.Progress):
	def progress(self):
		""" Do things. """
		
		self.parent.progress_wait_for_quota()
		
		self.parent.progress_set_text(_("Removing live-specific packages..."))

		try:
			# Configure
			self.parent.moduleclass.install.configure()
			
			verbose("  Removing %s" % " ".join(self.parent.moduleclass.packages))
			
			self.parent.moduleclass.install.remove_with_triggers(self.parent.moduleclass.packages)
			self.parent.progress_set_percentage(1)
		finally:
			# Exit
			self.parent.moduleclass.install.close()


class Frontend(glade.Frontend):
	def ready(self):
		""" Start the frontend """

		verbose("Removing live-specific packages...")
		self.set_header("hold", _("Removing live-specific packages..."), _("This may take a while."))
		
		self.progress_set_quota(1)
	
	def process(self):
		
		clss = Remove(self)
		clss.start()
