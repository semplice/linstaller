# -*- coding: utf-8 -*-
# linstaller welcome module frontend - (C) 2011-12 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.frontends.glade as glade
import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import warn,info,verbose,root_check		

#from gi.repository import Gtk

class Frontend(glade.Frontend):
	def ready(self):
		# Set header
		self.set_header("info", _("Welcome!"), _("Welcome to the %s installation wizard!") % self.moduleclass.main_settings["distro"], appicon="gtk-save")
		
		# Disable back button, this MUST be the first page
		self.idle_add(self.objects["parent"].back_button.set_sensitive, False)
		
		if not self.is_module_virgin:
			return
		
