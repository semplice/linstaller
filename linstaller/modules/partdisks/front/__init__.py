# -*- coding: utf-8 -*-
# linstaller partdisks module frontend - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.module as module

class Module(module.Module):
	def seedpre(self):
		""" Caches variables used by this module. """
		
		self.cache("root")
		self.cache("root_filesystem")
		self.cache("root_noformat")
		self.cache("root_override")
		self.cache("swap")
		self.cache("swap_noformat")
		self.cache("skip_to_selection")
		self.cache("onlyusb")
		self.cache("is_echo", False)
		
		# Encryption
		self.cache("cipher", "aes-xts-plain64")
		self.cache("keysize", "512")
		
		# Internal
		self.cache("changed")
