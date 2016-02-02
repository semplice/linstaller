# -*- coding: utf-8 -*-
# linstaller finish module install - (C) 2014 Eugenio "g7" Paolantonio
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.module as module
import linstaller.core.main as m

import os

class Install(module.Install):

	def update_initramfs(self):
		"""
		Updates the initramfs.
		"""
		
		m.verbose("Updating the initramfs...")
		m.sexec("update-initramfs -u -k all")

	def create_ssl_certs(self):
		"""
		Creates the missing SSL certs.
		"""
		
		if os.path.exists("/var/lib/dpkg/info/ssl-cert.list"):
			# FIXME: saner check?
			m.verbose("Creating SSL certs...")
			m.sexec("make-ssl-cert generate-default-snakeoil --force-overwrite")

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
			# Create missing certs
			self.install.create_ssl_certs()
		finally:
			# Exit
			self.install.close()
