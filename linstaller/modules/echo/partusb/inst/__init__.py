# -*- coding: utf-8 -*-
# linstaller echo.partusb module install - (C) 2012 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.module as module
import linstaller.core.main as m

from linstaller.core.main import verbose

import linstaller.core.libmodules.partdisks.library as lib

import os, shutil

class Module(module.Module):
	def create(self):
		""" Creates the persistent filesystem at TARGET/PATH/TYP-SUFFIX. """
				
		if not self.settings["size"]:
			self.settings["size"] = self.modules_settings["echo.partusb"]["size"]
		
		path = self.main_settings["target"] + self.settings["path"] # os.path.join doesn't work if second argument begins with /
		image = os.path.join(path, "persistence-%s" % (self.settings["suffix"]))
		
		# Create path if it doesn't exist
		if not os.path.exists(path): os.makedirs(path)
		
		# Generate an empty file, of the desired size.
		#m.sexec("dd if=/dev/zero of=%s bs=1MB count=%s" % (image, self.settings["size"]))
		verbose("Generating empty file...")
		
		with open(image, "w") as f:
			f.seek((int(self.settings["size"]) * 1024 * 1024) -1)
			f.write("\x00")
		

	def format(self):
		""" Formats the previously created persistent filesystem. """
			
		path = self.main_settings["target"] + self.settings["path"] # os.path.join doesn't work if second argument begins with /
		image = os.path.join(path, "persistence-%s" % (self.settings["suffix"]))
		
		# Format
		m.sexec("mkfs.ext2 -F %s" % image)
	
	def configure(self):
		""" Configures the previously formatted persistent filesystem. """
		
		path = self.main_settings["target"] + self.settings["path"] # os.path.join doesn't work if second argument begins with /
		image = os.path.join(path, "persistence-%s" % (self.settings["suffix"]))
		
		# Mount
		mpoint = lib.mount_partition(path=image, opts="loop")
		
		if self.settings["type"] in ("root", "home"):
			# Write
			with open(os.path.join(mpoint, "persistence.conf"), "w") as f:
				if self.settings["type"] == "root":
					# root persistence
					f.write("/ union\n")
				elif self.settings["type"] == "home":
					# home persistence
					f.write("/ bind\n")
		else:
			# We need to copy the path specified in type as the persistence.conf in the mountpoint
			shutil.copy2(self.settings["type"], os.path.join(mpoint, "persistence.conf"))
		
		# Umount!
		lib.umount(path=mpoint)
			
		
	def seedpre(self):
		""" Cache preseeds. """
		
		self.cache("path", "/persistent")
		self.cache("size")
		self.cache("suffix","live")
		self.cache("type","root") # FIXME: something wrong here... should use the type set on the front...
