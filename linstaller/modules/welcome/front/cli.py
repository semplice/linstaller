# -*- coding: utf-8 -*-
# linstaller welcome module frontend - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.frontends.cli as cli
import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import warn,info,verbose,root_check

class Frontend(cli.Frontend):
	def start(self):
		""" Start the frontend """

		# Check if we are root...
		root_check()

		self.header(_("Welcome!"))
		
		print(_("Welcome to the %s installation wizard!") % self.moduleclass.main_settings["distro"])
		print
		print(_("This wizard will help you with the installation of the distribution into your Hard Disk or another removable media."))
		print(_("Keep in mind that this installer it's still in testing phase."))
		print(_("Please reports any problem at http://bugs.launchpad.net/linstaller."))
		print
		
		# We should continue?
		res = self.question(_("Do you want to begin installation?"), default=True)
		if not res: self.end()
		
		verbose("Starting installation prompts.")
