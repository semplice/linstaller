# -*- coding: utf-8 -*-
# linstaller bootloader module frontend - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.frontends.cli as cli
import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import warn,info,verbose

class Frontend(cli.Frontend):
	def start(self):
		""" Start the frontend """
		
		self.header(_("Bootloader"))

						
		print(_("The bootloader is that piece of software that lets you boot your %(distroname)s system.") % {"distroname":self.moduleclass.main_settings["distro"]})
		print(_("Without the bootloader, you can't boot %(distroname)s.") % {"distroname":self.moduleclass.main_settings["distro"]})
		print
		## BOOTLOADER SELECTION
		if not self.settings["bootloader"]:
			# Ask for bootloader
			result = self.entry(_("Which bootloader do you want to install? [press ENTER for 'grub']"),blank=True)
			if result in ("grub"):
				self.settings["bootloader"] = result
			elif not result:
				# Default (grub)
				self.settings["bootloader"] = "grub"
			else:
				_fake = self.entry(_("Invalid bootloader specified. [press ENTER to continue]"),blank=True)
				return "restart"
			print
		
		## DEVICE SELECTION
		if not self.settings["device"] and not ("uefidetect.inst" in self.moduleclass.modules_settings and self.moduleclass.modules_settings["uefidetect.inst"]["uefi"] == True):
			print(_("You can choose to install the bootloader into the Master Boot Record of your hard disk. This is recommended."))
			print(_("If you choose 'No', it will be installed on your root partition.") + "\n")
			
			result = self.question(_("Do you want to install the bootloader into the MBR?"), default=True)
			if result:
				# Yay
				self.settings["device"] = "mbr"
			else:
				# Root
				self.settings["device"] = "root"
		
		verbose("Bootloader %s will be installed in %s" % (self.settings["bootloader"], self.settings["device"]))
