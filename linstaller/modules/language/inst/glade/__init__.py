# -*- coding: utf-8 -*-
# linstaller language module install - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
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
		language = self.parent.moduleclass.modules_settings["language"]["language"]
		layout = self.parent.moduleclass.modules_settings["language"]["layout"]
		model = self.parent.moduleclass.modules_settings["language"]["model"]
		variant = self.parent.moduleclass.modules_settings["language"]["variant"]

		savespace = self.parent.moduleclass.modules_settings["language"]["savespace"]
		savespace_purge = self.parent.moduleclass.modules_settings["language"]["savespace_purge"]

		try:
			self.parent.progress_set_text(_("Setting language..."))
			self.parent.moduleclass.install.language(language)
			self.parent.progress_set_percentage(1)

			# Set savespace, if any...
			if savespace:
				self.parent.progress_set_text(_("Enabling 'Save space' feature..."))
				self.parent.moduleclass.install.savespace(language)
				self.parent.progress_set_percentage(2)
				
				if savespace_purge:
					self.parent.progress_set_text(_("Removing older translations... This may take a while."))
					self.parent.moduleclass.install.purge(language)
					self.parent.progress_set_percentage(3)

			self.parent.progress_set_text(_("Setting keyboard..."))
			self.parent.moduleclass.install.keyboard(layout=layout, model=model, variant=variant)
			self.parent.progress_set_percentage(4)
		finally:
			# Exit
			self.parent.moduleclass.install.close()


class Frontend(glade.Frontend):
	def ready(self):
		""" Start the frontend """

		verbose("Setting language and keyboard")
		self.set_header("hold", _("Setting language and keyboard..."), _("This may take a while."))
		
		self.progress_set_quota(4)
	
	def process(self):
		
		clss = Set(self)
		clss.start()
