# -*- coding: utf-8 -*-
# linstaller update module frontend - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

# WARNING: This is a debian-related module!

import linstaller.frontends.gtk3 as gtk3
import linstaller.core.main as m
import t9n.library
_ = t9n.library.translation_init("linstaller")

import apt.cache as cache

from linstaller.core.main import warn,info,verbose

class Frontend(gtk3.Frontend):
	def gtk_start(self):
		""" Start the frontend """
		
		verbose("packages are: %s" % self.settings["packages"])
		
		self.window.set_header("info", _("Installer updates"), _("Update the installer"))
		
		self.window.text_new(_("%(distroname)s's installer improves every day.") % {"distroname":self.moduleclass.main_settings["distro"]})
		self.window.text_new(_("It is good measure to have the latest version before installing the distribution.") + "\n")
		
		self.cbox = self.window.checkbox(_("The installer should check for updates."), default=True)
	
	def on_next(self):
		""" Override for the on_next function. """
		
		status = self.cbox.get_active() # Get status.
		if status:
			# Do checking
					
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
			self.window.set_header("ok", _("Installer updated"), _("Everything went well"))
			
			print(_("The installer packages have been updated successfully.") + "\n")
			
			result = self.entry(_("Press ENTER to start the updated installer"), blank=True)
			return "fullrestart"

