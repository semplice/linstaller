# -*- coding: utf-8 -*-
# linstaller timezone module frontend - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.module as module

class Module(module.Module):
	def seedpre(self):
		""" Caches variables used by this module. """
		
		self.cache("userfullname")
		self.cache("username")
		self.cache("password")
		self.cache("password_min_chars", "4")
		self.cache("root")
		self.cache("rootpassword")
		self.cache("hostname")

	def check(self, what, string):
		""" Checks if a hostname/username is valid. """
		
		if what == "hostname":
			ALLOWED_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.-"
		else:
			ALLOWED_CHARS = "abcdefghijklmnopqrstuvwxyz0123456789.-"
		
		unallowed = []
		for lettera in string:
			if lettera not in ALLOWED_CHARS and '" %s "' % lettera not in unallowed:
				unallowed.append('" %s "' % lettera)

		if unallowed:
			return unallowed
		else:
			return True
