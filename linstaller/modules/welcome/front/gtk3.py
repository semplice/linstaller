# -*- coding: utf-8 -*-
# linstaller welcome module frontend - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.frontends.cli as cli
import linstaller.frontends.gtk3 as gtk3
import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import warn,info,verbose,root_check

class Frontend(gtk3.Frontend):
	def start(self):
		""" Start the frontend """
		
		# Check if we are root...
		root_check()
		
		self.window.set_header("info", _("Welcome!"), "")
		
		self.window.text_new(_("Welcome to the %s installation wizard!") % self.moduleclass.main_settings["distro"])
		self.window.text_new()
		self.window.text_new(_("This wizard will help you with the installation of the distribution into your Hard Disk or another removable media."))
		self.window.text_new(_("Keep in mind that this installer it's still in testing phase."))
		self.window.text_new(_("Please reports any problem at http://bugs.launchpad.net/linstaller."))
		self.window.text_new()
		
		self.window.reset_position()
		gtk3.Gtk.main()

		verbose("Starting installation prompts.")
