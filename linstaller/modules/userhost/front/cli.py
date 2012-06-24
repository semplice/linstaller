# -*- coding: utf-8 -*-
# linstaller timezone module frontend - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.frontends.cli as cli
import linstaller.core.main as m
import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import warn,info,verbose

class Frontend(cli.Frontend):
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
		if not self.settings["root"] == None:
			if not self.settings["root"]:
				res = self.question(_("Do you want to enable root account?"), default=False)
			else:
				res = True
			if res and not self.settings["rootpassword"]:
				self.settings["rootpassword"] = self.password_prompt(_("root's password"))
				self.settings["root"] = True
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
		""" Checks the username/hostname. """
		
		string = self.entry(text)
		
		result = self.moduleclass.check(what, string)
		if result == True:
			return string
		else:
			warn(_("You can't use these chars in the %s, please re-try: ") % (what) + str(result))
			return self.check(what, text)
	
	def password_prompt(self, text):
		""" A simple password prompt """
		
		passw1 = self.entry(text, password=True)
		if len(passw1) < int(self.settings["password_min_chars"]):
			warn(_("The password should be composed of at least %s charchters.") % self.settings["password_min_chars"])
			return self.password_prompt(text)
		passw2 = self.entry(text + _(" (again)"), password=True)
		
		if not passw1 == passw2:
			# Wrong!
			warn(_("The passwords doesn't match! Please retry."))
			return self.password_prompt(text)
		else:
			return passw1
