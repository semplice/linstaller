# -*- coding: utf-8 -*-
# linstaller debian module install - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.frontends.cli as cli
import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import warn,info,verbose

# NOTE: This is a debian-specific module.

class Frontend(cli.Frontend):
	def start(self):
		""" Start the frontend """

		verbose("Removing live-specific packages...")
		
		# Get a progressbar
		progress = self.progressbar(_("Removing live-specific packages:"), 1)

		# Start progressbar
		progress.start()

		try:
			# Configure
			self.moduleclass.install.configure()
			
			verbose("  Removing %s" % " ".join(self.moduleclass.packages))
			
			self.moduleclass.install.remove_with_triggers(self.moduleclass.packages)
			progress.update(1)
		finally:
			# Exit
			self.moduleclass.install.close()
		
		progress.finish()
