# -*- coding: utf-8 -*-
# linstaller echo.partusb module install - (C) 2012 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.module as module
import linstaller.core.main as m

from linstaller.core.main import verbose

import os

class Module(module.Module):
	def create(self):
		""" Creates the persistent filesystem at /linstaller/target/PATH/TYP-SUFFIX. """
		
		if not self.settings["type"]:
			self.settings["type"] = "live-rw"
				
		if not self.settings["size"]:
			self.settings["size"] = self.modules_settings["echo.partusb"]["size"]
		
		path = "/linstaller/target" + self.settings["path"] # os.path.join doesn't work if second argument begins with /
		image = os.path.join(path, "%s-%s" % (self.settings["type"], self.settings["suffix"]))
		
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

		if not self.settings["type"]:
			self.settings["type"] = "live-rw"
			
		path = "/linstaller/target" + self.settings["path"] # os.path.join doesn't work if second argument begins with /
		image = os.path.join(path, "%s-%s" % (self.settings["type"], self.settings["suffix"]))
		
		# Format
		m.sexec("mkfs.ext2 -F %s" % image)
		
	def seedpre(self):
		""" Cache preseeds. """
		
		self.cache("path", "/persistent")
		self.cache("size")
		self.cache("suffix","live")
		self.cache("type")
