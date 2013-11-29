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
	
	header_title = _("Bootloader")
	header_subtitle = _("Bootloader settings")
	header_icon = "drive-harddisk"
	
	def pre_ready(self):

		if (self.is_module_virgin and self.settings["device"] != False) or ("uefidetect.inst" in self.moduleclass.modules_settings and self.moduleclass.modules_settings["uefidetect.inst"]["uefi"] == True) or self.settings["skip"] or self.settings["caspered"] == True:
			# Selected device, do not prompt or UEFI.
			if self.is_module_virgin:
				# Ensure we say that on the virgin state casper has been executed
				self.settings["caspered"] = True
			self.module_casper()
	
	def ready(self):
		
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
			_("If the root partition is a LVM Logical Volume, you are strongly encouraged to install the bootloader into the MBR."),
			_("Otherwise, the installer will automatically install the bootloader into the /boot partition, if supplied."),
			_("If the /boot partition is a LVM Logical Volume too, the bootloader installation will be skipped."),
			"",
			_("You can force the device where to install the bootloader by using the :bootloader:forcedevice seed."),
			"",
		)

		# Properly set it
		text.set_markup("\n".join(label))
		
	
	def on_module_change(self):
		""" Proper set settings["device"] when Next button has been clicked. """
		
		value = self.onmbr.get_active()
		if value and not self.settings["forcedevice"]:
			# Yay
			self.settings["device"] = "mbr"
		elif not self.settings["forcedevice"]:
			
			# Check if the partition is an LVM LV...
			if len(self.moduleclass.modules_settings["partdisks"]["root"].split("/")) > 3:
				# Is on a LVM VG, so it's for sure a LV
				
				verbose("Root partition is a LVM LV, searching for /boot")
				
				self.settings["device"] = "pending"
				
				# Check for /boot
				for device, value in self.moduleclass.modules_settings["partdisks"]["changed"].items():
					if "useas" in value["changes"] and value["changes"]["useas"] == "/boot":
						# Found!
						if len(device.split("/")) <= 3:
							# Not on LVM! Good to know, force this device
							verbose("Boot partition found, installing bootloader there")
							self.settings["device"] = device
						break
				
				if self.settings["device"] == "pending":
					# Nothing, sorry :(
					verbose("Skipping bootloader installation as no unencrypted /boot found")
					self.settings["skip"] = True
					self.settings["device"] = False
			else:			
				# Root
				self.settings["device"] = "root"
		else:
			# Forced
			self.settings["device"] = self.settings["forcedevice"]
			
		if not self.settings["skip"]:
			verbose("Bootloader %s will be installed in %s" % (self.settings["bootloader"], self.settings["device"]))
		
		return None
