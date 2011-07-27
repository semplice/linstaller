# -*- coding: utf-8 -*-
# linstaller partdisks module install - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.cli_frontend as cli
import linstaller.core.module as module
import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import warn,info,verbose
import linstaller.core.libmodules.partdisks.library as lib

import os

class Module(module.Module):
	def start(self):
		""" Start override to unsquash. """
		
		# Mount root partition.
		root = self.modules_settings["partdisks"]["root"]
		
		# Ensure that is unmounted
		if os.path.ismount("/linstaller/target"):
			# Target mounted. Unmount
			lib.umount(path="/linstaller/target")
		if lib.is_mounted(root):
			# Partition mounted. Unmount
			lib.umount(path=root)
		
		# Then mount at TARGET
		lib.mount_partition(path=root, target="/linstaller/target")
