# -*- coding: utf-8 -*-
# linstaller network module install - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.main as m
import linstaller.core.module as module
import shutil

import os

class Install(module.Install):
	def copy_resolvconf(self):
		""" Copies host /etc/resolv.conf to target.
		Required to use mirrorselect.
		MUST BE CALLED AFTER CLOSING THE CHROOT!
		"""
		
		shutil.copy2("/etc/resolv.conf", os.path.join(self.moduleclass.main_settings["target"], "etc/resolv.conf"))

	def configure(self):
		""" Configures network. """
		
		# /etc/resolv.conf
		#with open("/etc/resolv.conf", "w"):
		#	pass

		# /etc/network/interfaces (configure loopback)
		with open("/etc/network/interfaces", "w") as interfaces:
			interfaces.write("""# The loopback network interface
auto lo
iface lo inet loopback
""")

class Module(module.Module):
	def _associate_(self):
		""" Shut up associate as we do not have any frontend. """
		
		pass

	def start(self):
		""" Start module """
		
		self.install = Install(self)
		
		m.verbose("Configuring networking...")
		
		try:
			# NETWORKING: set.
			self.install.configure()
		finally:
			# Exit
			self.install.close()
			# Copy resolv.conf
			self.install.copy_resolvconf()
		
