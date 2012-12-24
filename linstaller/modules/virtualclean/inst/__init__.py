# -*- coding: utf-8 -*-
# linstaller virtualclean module install - (C) 2012 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.module as module
import linstaller.core.main as m

import commands

class Install(module.Install):

	@property
	def type(self):
		""" Returns the type of the Virtual Machine (returns None if the system is physical). """
		
		typ = commands.getoutput("imvirt")
		if typ == "Physical":
			return None
		else:
			return typ
	
	def remove_virtualbox(self):
		""" Removes VirtualBox-related packages. """
		
		# FIXME: New releases of linstaller should handle better the package checking.
		
		try:
			for pkg in self.settings["remove-virtualbox.inst"].split(" "):
				m.sexec("dpkg -l %s &> /dev/null" % pkg, shell=True)
		except:
			return
		
		m.sexec("apt-get remove --yes --force-yes --purge %s" % self.settings["remove-virtualbox"])

	def remove(self, typ):
		""" Removes the virtual-related packages we do not need. """
		
		if typ != "VirtualBox":
			# We can remove virtualbox-related packages
			self.remove_virtualbox()

class Module(module.Module):
	def start(self):
		""" Start module """

		self.install = Install(self)
		
		module.Module.start(self)
	
	def seedpre(self):
		""" Cache configuration """
		
		self.cache("remove-virtualbox", "virtualbox-guest-x11 virtualbox-guest-utils")
