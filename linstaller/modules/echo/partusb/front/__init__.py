# -*- coding: utf-8 -*-
# linstaller echo.partusb module frontend - (C) 2012 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.module as module
import linstaller.core.libmodules.partdisks.library as lib

import os

class Module(module.Module):
	def freespace(self, partition):
		""" Calculates freespace on partition. """
		
		# Rapid-mount
		mounted = lib.mount_partition(path=partition)
		
		info = os.statvfs(mounted)

		free = info.f_frsize * info.f_bavail
		
		# Umount
		lib.umount(path=mounted)
		
		return free
	
	def is_fat(self, partition):
		""" Returns True if the partition (str) is a fat32 partition. False if not. """
		
		part = lib.return_partition(partition)
		fs = part.fileSystem.type
		
		if fs in ("fat16", "fat32"):
			return True
		
		return False

	def dirsize(self, directory):
		""" Returns the size of a directory. """
		
		size = 0
		for dirs, dirn, filen in os.walk(directory):
			for f in filen:
				size += os.path.getsize(os.path.join(dirs, f))
		
		return size
		
	def seedpre(self):
		""" Caches variables used by this module. """
		
		self.cache("size")
		self.cache("allfreespace")
