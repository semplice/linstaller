# -*- coding: utf-8 -*-
# linstaller timezone module frontend - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.cli_frontend as cli
import linstaller.core.main as m
import linstaller.core.module as module
import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import warn,info,verbose

class CLIFrontend(cli.CLIFrontend):
	def start(self):
		""" Start the frontend """
		
		self.header(_("Users & Hostname"))
		
		# Users
		if not self.settings["userfullname"]:
			self.settings["userfullname"] = self.entry(_("New user's full name (e.g. John Doe)"))
		if not self.settings["username"]:
			self.settings["username"] = self.check("username", _("%s's username (no spaces; e.g: john)") % self.settings["userfullname"])
			print
		
		verbose("Selected username %s (%s)." % (self.settings["username"], self.settings["userfullname"]))
		
		# Passwords
		if not self.settings["password"]:
			self.settings["password"] = self.password_prompt(_("%s's password") % self.settings["userfullname"])
			print
		
		verbose("Selected password.")
		
		# Root
		if not self.settings["root"] or self.settings["root"] != "False":
			if not self.settings["root"] == "True":
				res = self.question(_("Do you want to enable root account?"), default=False)
			else:
				res = True
			if res and not self.settings["rootpassword"]:
				self.settings["rootpassword"] = self.password_prompt(_("root's password"))
				self.settings["root"] = "True"
				verbose("Selected root password.")
			elif not res:
				verbose("Root disabled.")
			else:
				verbose("preseeded root password.")
			print
		else:
			verbose("Root disabled.")
		
		
		# Hostname
		if not self.settings["hostname"]:
			self.settings["hostname"] = self.check("hostname", _("Computer's name (e.g. johndesktop)"))
		
		verbose("Selected hostname %s." % self.settings["hostname"])
			
	def check(self, what, text):
		""" Checks if a hostname/username is valid. """
		
		if what == "hostname":
			ALLOWED_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.-"
		else:
			ALLOWED_CHARS = "abcdefghijklmnopqrstuvwxyz0123456789.-"
		
		string = self.entry(text)
		
		unallowed = []
		for lettera in string:
			if lettera not in ALLOWED_CHARS:
				unallowed += lettera

		if unallowed:
			warn(_("You can't use these chars in the %s, please re-try: ") % (what) + str(unallowed))
			return self.check(what, text)
		else:
			return string
	
	def password_prompt(self, text):
		""" A simple password prompt """
		
		passw1 = self.entry(text, password=True)
		if len(passw1) < 6:
			# Pasword lenght is lesser than six
			warn(_("The password should be composed from at least six charchters."))
			return self.password_prompt(text)
		passw2 = self.entry(text + _(" (again)"), password=True)
		
		if not passw1 == passw2:
			# Wrong!
			warn(_("The password aren't the same! Please re-try."))
			return self.password_prompt(text)
		else:
			return passw1

	
class Module(module.Module):
	def _associate_(self):
		""" Associate frontends. """
		
		self._frontends = {"cli":CLIFrontend}
	
	def seedpre(self):
		""" Caches variables used by this module. """
		
		self.cache("userfullname")
		self.cache("username")
		self.cache("password")
		self.cache("root")
		self.cache("rootpassword")
		self.cache("hostname")
