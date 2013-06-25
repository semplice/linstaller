# -*- coding: utf-8 -*-
# linstaller echo.configure module install - (C) 2012 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.module as module
import linstaller.core.main as m

import shutil
import os

class Module(module.Module):	
	def _associate_(self):
		""" Shut up associate as we do not have any frontend. """
		
		pass
	
	def start(self):
		""" Configure syslinux. """
		
		self.path = self.modules_settings["echo.partusb.inst"]["path"]
		if self.path[-1] != "/":
			self.path = self.path + "/"
		self.image_path = self.modules_settings["echo"]["image_path"]
		self.part_suffix = self.modules_settings["echo.partusb.inst"]["suffix"]
				
		args = []
		
		try:
			args.append("username=%s" % self.modules_settings["userhost"]["username"]) # Username
			args.append("hostname=%s" % self.modules_settings["userhost"]["hostname"]) # Hostname
			args.append("user-fullname=%s" % self.modules_settings["userhost"]["userfullname"]) # Userfullname
			
			args.append("locales=%s" % self.modules_settings["language"]["language"]) # Language
			args.append("keyboard-layouts=%s" % self.modules_settings["language"]["layout"]) # Language
			
			args.append("timezone=%s" % self.modules_settings["timezone"]["timezone"]) # Timezone
		except:
			# Failed to add arguments, do not worry: nothing important.
			pass
		
		args.append("quickreboot") # reboot without prompting
		args.append("quiet") # let's stay quiet
		
		# Here is where the magic happens:
		args.append("persistence") # tell live-boot to use persistence
		if not self.path == "/": args.append("persistence-path=%s" % self.path) # Directory where the image is stored, if any
		args.append("persistence-subtext=%s" % self.part_suffix) # subtext of the persistent image
		
		args.append("live-media-path=%s" % self.image_path) # path for the image
		
		# Rebuild live.cfg to include persistent.cfg...
		with open(os.path.join(self.main_settings["target"], "syslinux/live.cfg"), "w") as f:
			f.write("""include persistent.cfg
label nextboot
	menu label ^Next Boot Device
	localboot -1
	text help
  Boot the next device specified into the BIOS configuration.
	endtext

#label floppy
#	localboot 0x00

#label disk1
#	localboot 0x80

#label disk2
#	localboot 0x81

#label nextboot
#	localboot -1
""")

		# Finally rewrite persistent.cfg in syslinux with our configuration...
		if os.path.exists(os.path.join(self.main_settings["target"], "syslinux/persistent.cfg")):
			mode = "a" # Append.
		else:
			mode = "w"
		with open(os.path.join(self.main_settings["target"], "syslinux/persistent.cfg"), mode) as f:
			if mode == "w":
				f.write("""default usb
label usb
	menu label ^Live usb with persistence
	kernel %(path)s/vmlinuz
	append initrd=%(path)s/initrd.img boot=live config  %(args)s
	text help
   Boots the live usb with persistence. In most cases you should choose this item.
	endtext
""" % {"path":"/" + self.image_path,"args":" ".join(args)})

			elif mode == "a":
				f.write("""label usb-%(subtext)s
	menu label ^Live usb with persistence (%(subtext)s)
	kernel %(path)s/vmlinuz
	append initrd=%(path)s/initrd.img boot=live config  %(args)s
	text help
   Boots the live usb with persistence. In most cases you should choose this item.
	endtext
""" % {"path":"/" + self.image_path,"args":" ".join(args), "subtext":self.part_suffix})
