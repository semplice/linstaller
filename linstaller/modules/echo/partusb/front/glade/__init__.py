# -*- coding: utf-8 -*-
# linstaller echo.partusb module frontend - (C) 2012 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.frontends.glade as glade
import linstaller.core.main as m
import os
import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import warn,info,verbose

class Frontend(glade.Frontend):
	def ready(self):

		self.set_header("info", _("Persistence partition"), _("Select the size of the persistence partition"))
		
		if (self.is_module_virgin and self.settings["size"]) or self.settings["caspered"] == True:
			# size already selected, do not prompt.
			if self.is_module_virgin:
				# Ensure we say that on the virgin state casper has been executed
				self.settings["caspered"] = True
			self.module_casper()

		# Get adjustment
		self.size_adjust = self.objects["builder"].get_object("size_adjust")

		# Calculate free space
		part = self.moduleclass.modules_settings["partdisks"]["root"]
		freespace = self.moduleclass.freespace(part)
		is_fat = self.moduleclass.is_fat(part)
		
		# Get the size of the things we will copy during install...
		if not self.settings["allfreespace"]:
			size = 0
			size += os.path.getsize(self.moduleclass.modules_settings["echo"]["image"]) # Squashfs image
			size += os.path.getsize(self.moduleclass.modules_settings["echo"]["vmlinuz"]) # Kernel image
			size += os.path.getsize(self.moduleclass.modules_settings["echo"]["initrd"]) # Initrd image
			size += self.moduleclass.dirsize(self.moduleclass.modules_settings["echo"]["syslinux"]) # Syslinux directory
			# Then remove from freespace.
			freespace -= size
		
		# Convert to megabytes
		freespace = freespace / 1024 / 1024
		
		# Round freespace
		freespace = int(round(freespace))

		# Remove five megabytes from freespace, safe threshold to avoid problems when installing bootloader, etc.
		freespace -= 5

		# If is fat, our threshold is 4045 MB. Let's set it to 4040.
		if is_fat and freespace > 4040:
			freespace = 4040
		
		# Adjust size_adjust
		self.size_adjust.set_lower(10)
		self.size_adjust.set_upper(freespace)

		# If not virgin, just exit
		if not self.is_module_virgin:
			if self.size_adjust.get_value() > freespace:
				# If current value is bigger than freespace, we need to reset it.
				self.size_adjust.set_value(freespace)
			self.set_header("ok", _("You can continue!"), _("Press forward to continue."))
			return
		
		# Set size value
		self.size_adjust.set_value(freespace)

		# Get text label
		text = self.objects["builder"].get_object("text")
		
		# Format label:
		label = [
			_("You need to specify the size of the persistence partition."),
			_("The persistence partition will be stored as a file into the USB key and will contain all changes done to the stock system."),
			"",
		]
		
		if is_fat:
			label.append(_("Partition is a FAT partition, so there is a limit to a maximum of 4GiB per-file."))
			label.append("")

		# Properly set it
		text.set_markup("\n".join(label))

	def on_module_change(self):
		""" Proper set settings["size"] and settings["enable_sources"] when a button has been clicked. """
		
		self.settings["size"] = int(self.size_adjust.get_value())
		verbose("Selected size %s" % self.settings["size"])
		
		return None
	
