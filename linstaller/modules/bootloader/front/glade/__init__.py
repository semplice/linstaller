# -*- coding: utf-8 -*-
# linstaller bootloader module frontend - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.frontends.glade as glade
import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import warn,info,verbose

class Frontend(glade.Frontend):
	def ready(self):
		
		self.set_header("info", _("Bootloader"), _("Bootloader settings"))
		
		if (self.is_module_virgin and self.settings["device"] != False) or ("uefidetect.inst" in self.moduleclass.modules_settings and self.moduleclass.modules_settings["uefidetect.inst"]["uefi"] == True) or self.settings["caspered"] == True:
			# Selected device, do not prompt or UEFI.
			if self.is_module_virgin:
				# Ensure we say that on the virgin state casper has been executed
				self.settings["caspered"] = True
			self.module_casper()

		# Get the checkbox
		self.onmbr = self.objects["builder"].get_object("onmbr")

		if not self.is_module_virgin:
			self.set_header("ok", _("You can continue!"), _("Press forward to continue."))
			return

		# Get text label
		text = self.objects["builder"].get_object("text")
		
		# Format label:
		label = (
			_("The bootloader is that piece of software that lets you boot your %(distroname)s system.") % {"distroname":self.moduleclass.main_settings["distro"]},
			_("Without the bootloader, you can't boot %(distroname)s.") % {"distroname":self.moduleclass.main_settings["distro"]},
			"",
			_("You can choose to install the bootloader into the Master Boot Record of your hard disk. This is recommended."),
			_("If you do not want to install the bootloader into the MBR, it will be installed on your root partition."),
			"",
		)

		# Properly set it
		text.set_markup("\n".join(label))
		
	
	def on_module_change(self):
		""" Proper set settings["device"] when Next button has been clicked. """
		
		value = self.onmbr.get_active()
		if value:
			# Yay
			self.settings["device"] = "mbr"
		else:
			# Root
			self.settings["device"] = "root"
			
		verbose("Bootloader %s will be installed in %s" % (self.settings["bootloader"], self.settings["device"]))
		
		return None
