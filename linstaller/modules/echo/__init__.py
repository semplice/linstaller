# -*- coding: utf-8 -*-
# linstaller echo module install - (C) 2012 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.module as module

## ABOUT THIS MODULE:
# This is a fake module which is used to store shared echo settings.
# It needs to be executed *BEFORE* any other echo module.
## END

class Module(module.Module):
	def _associate_(self):
		""" Shut up associate as we do not have any frontend. """
		
		pass
	
	def start(self):
		""" Shut up associate as we are only seeding items. """
		
		pass
	
	def seedpre(self):
		""" Cache settings. """

		self.cache("image","/live/image/live/filesystem.squashfs")
		self.cache("vmlinuz","/live/image/live/vmlinuz")
		self.cache("initrd","/live/image/live/initrd.img")
		self.cache("image_path","live")
		self.cache("syslinux","/usr/share/syslinux/themes/semplice-pulse/syslinux-live")
