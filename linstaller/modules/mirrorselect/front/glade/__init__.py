# -*- coding: utf-8 -*-
# linstaller mirrorselect module frontend - (C) 2011-12 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.frontends.glade as glade
import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import warn,info,verbose,root_check		

class Frontend(glade.Frontend):
	def ready(self):
		
		self.set_header("info", _("Mirror selection"), _("Select the best mirror"))
		
		if (self.is_module_virgin and self.settings["check"] != False) or self.settings["caspered"] == True:
			# None or True, do not prompt.
			if self.is_module_virgin:
				# Ensure we say that on the virgin state casper has been executed
				self.settings["caspered"] = True
			self.module_casper()
				
		if not self.is_module_virgin:
			self.set_header("ok", _("You can continue!"), _("Press forward to continue."))
			return

		# Get text label
		text = self.objects["builder"].get_object("text")
		
		# Format label:
		label = (
			_("%(distroname)s has many mirrors worldwide.") % {"distroname":self.moduleclass.main_settings["distro"]},
			_("You can let the installer to test all mirrors and to find the fastest for your zone."),
			"",
			_("This requires a working internet connection."),
			"",
		)

		# Properly set it
		text.set_markup("\n".join(label))
		
		# Get the checkboxes
		mirrorselect = self.objects["builder"].get_object("mirrorselect")
		debsrc = self.objects["builder"].get_object("debsrc")
		
		# Hide the debsrc box if we need to
		if self.settings["enable_sources"] != None:
			debsrc.hide()

