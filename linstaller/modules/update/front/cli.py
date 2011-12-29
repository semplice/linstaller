# -*- coding: utf-8 -*-
# linstaller update module frontend - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

# WARNING: This is a debian-related module!

import linstaller.frontends.cli as cli
import linstaller.core.main as m
import t9n.library
_ = t9n.library.translation_init("linstaller")

import apt.cache as cache

from linstaller.core.main import warn,info,verbose

class Frontend(cli.Frontend):
	def start(self):
		""" Start the frontend """
		
		verbose("packages are: %s" % self.settings["packages"])
		
		self.header(_("Installer Updates"))
		
		print(_("%(distroname)s's installer improves every day.") % {"distroname":self.moduleclass.main_settings["distro"]})
		print(_("It is good measure to have the latest version before installing the distribution.") + "\n")
		
		result = self.question(_("Would you like to check for installer updates?"), default=True)
		if result:
			# Do checking.
			
			info(_("Updating APT cache..."))
			self.moduleclass.install.update()
			
			verbose("Opening the refreshed APT cache...")
			self.moduleclass.install.open()
			
			verbose("Checking if the packages have been updated...")
			res = self.moduleclass.install.check()
			if not res:
				info(_("No updates found."))
				return
			
			info("Upgrading packages... this may take a while.")

			try:
				self.moduleclass.install.upgrade()
			except:
				print
				warn("Something went wrong while updating packages.")
				info("A reboot is recommended in order to start a safe linstaller version.\n")
				
				result = self.question("Would you like to reboot now?", default=True)
				if result:
					return "kthxbye"
				else:
					return
			
			# Everything should be cool now.
			self.header(_("Installer updated"))
			
			print(_("The installer packages have been updated successfully.") + "\n")
			
			result = self.entry(_("Press ENTER to start the updated installer"), blank=True)
			return "fullrestart"

