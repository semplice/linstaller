# -*- coding: utf-8 -*-
# linstaller echo.copy module install - (C) 2012 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.module as module
import linstaller.core.main as m
import linstaller.core.libmodules.unsquash.library as lib

import shutil, os

class Module(module.Module):		
	def copy(self):
		""" Copies image to /linstaller/target/PATH/filesystem.squashfs. """
		
		path = os.path.join("/linstaller/target", self.settings["path"])
		
		# Create path if it doesn't exist
		if not os.path.exists(path): os.makedirs(path)
		if not os.path.isdir(path): raise m.UserError("%s is not a directory!" % path)

		image = os.path.join(path, "filesystem.squashfs")
		vmlinuz = os.path.join(path, "vmlinuz")
		initrd = os.path.join(path, "initrd.img")
		
		if os.path.exists(image): raise m.UserError("%s already exists!" % image)
		
		# Copy the image
		shutil.copy(self.settings["image"], image)
		
		# Copy vmlinuz and initrd
		shutil.copy(self.settings["vmlinuz"], vmlinuz)
		shutil.copy(self.settings["initrd"], initrd)
	
	def copy_syslinux(self):
		""" Copies syslinux configuration to /linstaller/target/syslinux """
		
		syslinux = "/linstaller/target/syslinux"
		
		if not os.path.exists(syslinux):
			# Copy the directory
			shutil.copytree(self.settings["syslinux"], syslinux)
				
	def seedpre(self):
		""" Cache preseeds. """
		
		self.cache("image","/live/image/live/filesystem.squashfs")
		self.cache("vmlinuz","/live/image/live/vmlinuz")
		self.cache("initrd","/live/image/live/initrd.img")
		self.cache("path","live")
		self.cache("syslinux","/usr/share/syslinux/themes/semplice-pulse/syslinux-live")
