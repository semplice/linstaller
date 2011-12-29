# -*- coding: utf-8 -*-
# linstaller unsquash module install - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
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

		# Get a progressbar
		progress = self.progressbar(_("Setting timezone:"), 100)
		
		verbose("Setting timezone")
		# Get timezone
		timezone = self.moduleclass.modules_settings["timezone"]["timezone"]
		
		progress.start() # Start progressbar	
		try:
			self.moduleclass.install.set(timezone)
		finally:
			self.moduleclass.install.close() # Exit
		
		progress.finish()
		
		verbose("New timezone is: %s." % timezone)
