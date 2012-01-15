# -*- coding: utf-8 -*-
# linstaller language module frontend - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
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
		
		self.header(_("Mirror selection"))
				
		if self.settings["check"] == False:
			
			print(_("%(distroname)s has many mirrors worldwide.") % {"distroname":self.moduleclass.main_settings["distro"]})
			print(_("You can let the installer to test all mirrors and to find the fastest for your zone."))
			print
			print(_("This requires a working internet connection."))
			print
			
			# We should continue?
			res = self.question(_("Do you want to check for the fastest mirror?"), default=True)
			if res:
				self.settings["check"] = True
			else:
				self.settings["check"] = None
			
			if self.settings["enable_sources"] == None:
				# Ask if we should enable deb-src entries
				res = self.question(_("Do you want to enable deb-src entries?"), default=False)
				if res:
					self.settings["enable_sources"] = True
				else:
					self.settings["enable_sources"] = None

