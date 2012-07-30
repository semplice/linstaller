# -*- coding: utf-8 -*-
# linstaller unsquash module install - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.frontends.cli as cli
import linstaller.core.main as m
import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import warn,info,verbose

class Frontend(cli.Frontend):
	def start(self):
		""" Start the frontend """

		# Get a progressbar
		progress = self.progressbar(_("Setting Language & Keyboard:"), 2)
		
		verbose("Setting language and keyboard")

		# Get.
		language = self.moduleclass.modules_settings["language"]["language"]
		layout = self.moduleclass.modules_settings["language"]["layout"]
		model = self.moduleclass.modules_settings["language"]["model"]
		variant = self.moduleclass.modules_settings["language"]["variant"]

		# Start progressbar
		progress.start()
		
		try:
			# Set language
			self.moduleclass.install.language(language)
			progress.update(1)
			
			# Set keyboard and model
			self.moduleclass.install.keyboard(layout=layout, model=model, variant=variant)
			progress.update(2)
		finally:
			# Exit from chroot
			self.moduleclass.install.close()	
		
		progress.finish()
		
		verbose("Done.")
