# -*- coding: utf-8 -*-
# linstaller echo.partusb module frontend - (C) 2012 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.frontends.cli as cli
import linstaller.core.main as m
import os
import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import warn,info,verbose

class Frontend(cli.Frontend):
	def start(self, warning=False):
		""" Start the frontend """
		
		self.header(_("Persistence partition"))
		
		if warning:
			warn(warning)
			print
		
		size = self.settings["size"]
		if size:
			# Size already selected, going ahead
			return
		
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
		
		print(_("You need to specify the size of the persistence partition."))
		print(_("The persistence partition will be stored as a file into the USB key and will contain all changes done to the stock system."))
		print
		print(_("Usable freespace: %s MiB") % freespace)
		if is_fat:
			print(_("Partition uses a FAT partition, so there is a limit to a maximum of 4GiB per-file."))
		print(_("You can insert the percentage of the partition (e.g: 50%) or the full size of the new partition, in megabytes.") + "\n")

		res = self.entry(_("Insert the value here"))
			
		if "%" in res and res != "100%":
			# This is a percentage, folks!
			res = res[:-1] # Drop last %
			try:
				res = float(res)
			except:
				# Not a number
				return self.start(warning=_("Wrong percentage specified!"))
			res = (res * freespace) / 100.0
		elif res == "100%":
			res = freespace
		else:
			if float(res) == freespace:
				# Full partition.
				res = freespace
			else:
				try:
					res = float(res)
				except:
					# Not a number
					return self.start(warning=_("Wrong value specified!"))

		# Round res
		res = round(res)

		# Check if we can grow the partition at the given size...
		if freespace < res:
			# No!
			return self.start(warning=_("Not enough space!"))

		self.settings["size"] = str(int(res))
		
		verbose("Selected size %s" % self.settings["size"])
	
