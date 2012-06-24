# -*- coding: utf-8 -*-
# linstaller raspberrypi module install - (C) 2012 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.module as module

from linstaller.core.main import warn,info,verbose

import os, shutil

class Module(module.Module):
	def _associate_(self):
		""" Shut up associate as we do not have any frontend. """
		
		pass
		
	def start(self):
		""" Start override to configure the raspberrypi. """
		
		# Remove /etc/semplice-live-mode
		if os.path.exists("/etc/semplice-live-mode"): os.remove("/etc/semplice-live-mode")

		# Restore proper lightdm configuration
		if os.path.exists("/etc/lightdm/lightdm.conf"):
			os.remove("/etc/lightdm/lightdm.conf")
			shutil.copy("/usr/share/semplice-default-settings/lightdm/lightdm.conf", "/etc/lightdm/lightdm.conf")
		
		# Remove root openbox configuration installed by builder...
		if os.path.exists("/root/.config/openbox"):
			shutil.rmtree("/root/.config/openbox")
		
