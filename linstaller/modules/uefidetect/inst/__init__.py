# -*- coding: utf-8 -*-
# linstaller uefidetect module install - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.module as module
import linstaller.core.main as m
import os

class Module(module.Module):
	def _associate_(self):
		""" Shut up associate as we do not have any frontend. """
		
		pass

	def start(self):
		""" Start module """
		
		# FIXME: We need to detect UEFI even when booting in BIOS emulation (is it possible?)
		if os.path.exists("/sys/firmware/efi"):
			m.verbose("UEFI Detected.")
			self.settings["uefi"] = True
		
	def seedpre(self):
		""" Cache settings. """
		
		self.cache("uefi", False)
