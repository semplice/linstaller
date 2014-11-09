# -*- coding: utf-8 -*-
# linstaller finish module install - (C) 2014 Eugenio "g7" Paolantonio
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.module as module
import linstaller.core.main as m

class Install(module.Install):

	def update_initramfs(self):
		"""
		Updates the initramfs.
		"""
		
		m.verbose("Updating the initramfs...")
		m.sexec("update-initramfs -u -k all")


class Module(module.Module):
	def _associate_(self):
		""" Shut up associate as we do not have any frontend. """
		
		pass

	def start(self):
		""" Start module """
		
		self.install = Install(self)
		
		m.verbose("Finishing up...")
		
		try:
			# Update initramfs
			self.install.update_initramfs()
		finally:
			# Exit
			self.install.close()
