# -*- coding: utf-8 -*-
# linstaller update module frontend - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.frontends.glade as glade
import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import warn,info,verbose

import threading, time

class Update(threading.Thread):
	def __init__(self, parent):
		
		self.parent = parent
		threading.Thread.__init__(self)
	
	def run(self):
		
		# Make the buttons insensitive
		self.parent.idle_add(self.parent.objects["parent"].next_button.set_sensitive, False)
		self.parent.idle_add(self.parent.objects["parent"].back_button.set_sensitive, False)
		self.parent.idle_add(self.parent.objects["parent"].cancel_button.set_sensitive, False)
		self.parent.idle_add(self.parent.check.set_sensitive, False)
		
		self.parent.set_header("hold", _("Updating APT cache..."), _("This may take a while."))
		self.parent.moduleclass.install.update()
			
		verbose("Opening the refreshed APT cache...")
		self.parent.moduleclass.install.open()
			
		verbose("Checking if the packages have been updated...")
		res = self.parent.moduleclass.install.check()
		if not res:
			self.parent.set_header("ok", _("No updates found."), _("It seems you are already up-to-date. Yay!"))
			self.quit()
			return
		else:
			self.parent.set_header("hold", _("Upgrading packages..."), _("This may take a while."))

			try:
				self.parent.moduleclass.install.upgrade()
			except:
				self.parent.set_header("error", _("Something went wrong while updating packages."), _("A reboot is needed in order to start a safe linstaller version."))
				self.quit("reboot")
				return
			
			# Everything should be cool now.
			self.parent.set_header("ok", _("Installer updated"), _("Press forward to start the updated installer."))
			
			self.quit("fullrestart")
	
	def quit(self, res="ok"):
		
		# Make the buttons sensitive
		self.parent.idle_add(self.parent.objects["parent"].next_button.set_sensitive, True)
		self.parent.idle_add(self.parent.objects["parent"].back_button.set_sensitive, True)
		self.parent.idle_add(self.parent.objects["parent"].cancel_button.set_sensitive, True)
		#self.parent.idle_add(self.parent.check.set_sensitive, True)
		self.parent.idle_add(self.parent.check.set_active, False)
		
		self.parent.has_the_update_process_ran = True
		
		if res == "reboot":
			self.parent.objects["parent"].change_next_button_to_reboot_button()
		elif res == "fullrestart":
			self.parent.objects["parent"].change_next_button_to_fullrestart_button()


class Frontend(glade.Frontend):
	def ready(self):
				
		self.has_the_update_process_ran = False
		
		verbose("packages are: %s" % self.settings["packages"])
		
		self.set_header("info", _("Installer updates"), _("Ensure you have the installer up-to-date."), appicon="system-software-update")

		# Get the checkbox
		self.check = self.objects["builder"].get_object("check")

		if not self.is_module_virgin:
			self.set_header("ok", _("You can continue!"), _("Press forward to continue."))
			return

		# Get text label
		text = self.objects["builder"].get_object("text")

		# Format label:
		label = (
			_("%(distroname)s's installer improves every day.") % {"distroname":self.moduleclass.main_settings["distro"]},
			_("It is good measure to have the latest version before installing the distribution."),
			"",
			_("You can choose to check for installer updates before continuing the installation."),
			"",
		)

		# Properly set it
		text.set_markup("\n".join(label))
	
	def on_next_button_click(self):
		""" Do things ;-). """
		
		if not self.is_module_virgin: return None
		
		value = self.check.get_active()
		if value:
			# We should go ahead and update, if we haven't.
			if not self.has_the_update_process_ran:
				clss = Update(self)
				clss.start()
				
				return True
			else:
				return None
		else:
			# No :(
			return None
