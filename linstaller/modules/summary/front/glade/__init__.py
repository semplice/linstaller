# -*- coding: utf-8 -*-
# linstaller summary module frontend - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.frontends.glade as glade
import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import warn,info,verbose

import threading, time

class Frontend(glade.Frontend):
	
	header_title = _("Summary")
	header_subtitle = _("Please review everything before continuing.")
	header_icon = "emblem-default"
	
	def ready(self):
				
		if not self.is_module_virgin:
			self.set_header("ok", _("You can continue!"), _("Press forward to continue."))

		# Get labels
		partdisks_frame = self.objects["builder"].get_object("partdisks_frame")
		partitions = self.objects["builder"].get_object("partitions")
		
		keeptalking_frame = self.objects["builder"].get_object("keeptalking_frame")
		locale = self.objects["builder"].get_object("locale")
		keyboard = self.objects["builder"].get_object("keyboard")
		timezone = self.objects["builder"].get_object("timezone")
		name = self.objects["builder"].get_object("name")
		
		userhost_frame = self.objects["builder"].get_object("userhost_frame")
		username = self.objects["builder"].get_object("username")
		root = self.objects["builder"].get_object("root")
		hostname = self.objects["builder"].get_object("hostname")
		
		bootloader_frame = self.objects["builder"].get_object("bootloader_frame")
		bootloader = self.objects["builder"].get_object("bootloader")
		target = self.objects["builder"].get_object("target")


		# Parse changed partitions
		if "partdisks" in self.moduleclass.modules_settings:
			changed = self.moduleclass.modules_settings["partdisks"]["changed"]
			
			final_text = []
			
			for obj, value in changed.items():
				obj = str(obj)
				try:
					fs = str(value["obj"].fileSystem.type)
					mountpoint = value["changes"]["useas"]
					
					# If /, tell the user that the distribution will be installed here
					if mountpoint == "/":
						text = ": " + ("<b>" + _("%(distroname)s will be installed here.") % {"distroname":self.moduleclass.main_settings["distro"]} + "</b>")
					else:
						text = ""
					
					final_text.append(_(" - %(part)s (%(filesystem)s, mounts on %(mountpoint)s)%(text)s") % {"part":obj, "filesystem":fs, "mountpoint":mountpoint, "text":text})
				except:
					verbose("Unable to print details for %s" % obj)
			
			partitions.set_markup("\n".join(final_text))
		else:
			partdisks_frame.hide()
		
		
		# USB-Persistence
		#try:
		#	size = self.moduleclass.modules_settings["echo.partusb"]["size"]
		#	print(_("The persistence partion will be of %s MB.") % size)
		#	print
		#except:
		#	pass
				
		if not "language" in self.moduleclass.modules_settings and not "timezone" in self.moduleclass.modules_settings:
			keeptalking_frame.hide()
		else:
			if not "language" in self.moduleclass.modules_settings:
				locale.hide()
				keyboard.hide()
			elif not "timezone" in self.moduleclass.modules_settings:
				timezone.hide()
			
			if "language" in self.moduleclass.modules_settings:
				locale.set_text(self.moduleclass.modules_settings["language"]["language"])
				keyboard.set_text(",".join(self.moduleclass.modules_settings["language"]["layout"]) + " " + _("(model %s; variant %s)") % (self.moduleclass.modules_settings["language"]["model"], self.moduleclass.modules_settings["language"]["variant"]))
			if "timezone" in self.moduleclass.modules_settings:
				timezone.set_text(self.moduleclass.modules_settings["timezone"]["timezone"])

		
		if not "userhost" in self.moduleclass.modules_settings:
			userhost_frame.hide()
		else:
			name.set_text(self.moduleclass.modules_settings["userhost"]["userfullname"])
			username.set_text(self.moduleclass.modules_settings["userhost"]["username"])
			if self.moduleclass.modules_settings["userhost"]["root"]:
				root.set_text(_("Yes"))
			else:
				root.set_text(_("No"))
			hostname.set_text(self.moduleclass.modules_settings["userhost"]["hostname"])
		
		if not "bootloader" in self.moduleclass.modules_settings or ("uefidetect.inst" in self.moduleclass.modules_settings and self.moduleclass.modules_settings["uefidetect.inst"]["uefi"] == True) or self.moduleclass.modules_settings["bootloader"]["skip"]:
			bootloader_frame.hide()
		else:
			bootloader.set_text(self.moduleclass.modules_settings["bootloader"]["bootloader"])
			target.set_text(self.moduleclass.modules_settings["bootloader"]["device"])

	def on_next_button_click(self):
		verbose("Beginning installation.")
		
