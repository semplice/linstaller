# -*- coding: utf-8 -*-
# linstaller echo.partusb module install - (C) 2012 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.module as module
import linstaller.core.main as m

import os

class Module(module.Module):
	def create(self, typ="live-rw"):
		""" Creates the persistent filesystem at /linstaller/target/PATH/TYP-SUFFIX. """
		
		path = "/linstaller/target" + self.settings["path"] # os.path.join doesn't work if second argument begins with /
		image = os.path.join(path, "%s-%s" % (typ, self.settings["suffix"]))
		
		# Create path if it doesn't exist
		if not os.path.exists(path): os.makedirs(path)
		
		# Generate an empty file, of the desired size.
		m.sexec("dd if=/dev/null of=%s bs=%s seek=1" % (image, self.settings["size"]))

	def format(self, typ="live-rw"):
		""" Formats the previously created persistent filesystem. """
		
		path = "/linstaller/target" + self.settings["path"] # os.path.join doesn't work if second argument begins with /
		image = os.path.join(path, "%s-%s" % (typ, self.settings["suffix"]))
		
		# Format
		m.sexec("mkfs.ext2 -F %s" % image)
		
	def seedpre(self):
		""" Cache preseeds. """
		
		self.cache("path", "/persistent")
		self.cache("size", "1G")
		self.cache("suffix","live")
