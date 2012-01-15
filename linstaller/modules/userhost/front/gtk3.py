# -*- coding: utf-8 -*-
# linstaller timezone module frontend - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.frontends.gtk3 as gtk3
import linstaller.core.main as m
import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import warn,info,verbose

class Frontend(gtk3.Frontend):
	def start(self):
		""" Start the frontend """
		
		self.window.set_header("info", _("Users & Hostname"), _("Set users and hostname"))
		
		# Initial user
		userfullname_container, userfullname = self.window.entry(_("New user's full name (e.g. John Doe)"))
		username_container, username = self.window.entry(_("%s's username (no spaces; e.g: john)") % self.settings["userfullname"])
		self.window.text_new()
		
		# Passwords
		password1, password2 = self.window.password_entry_with_confirm(_("%s's password") % self.settings["userfullname"])
		self.window.text_new()
		
		password1_container, password1 = password1
		password2_container, password2 = password2
		
		# Root
		root_switch_container, root_switch = self.window.switch(_("Do you want to enable root account?"), default=False)
		root_password1, root_password2 = self.window.password_entry_with_confirm(_("root's password"))
		
		root_password1_container, root_password1 = root_password1 # Split the confirms
		root_password2_container, root_password2 = root_password2 # Same.

		# Hostname
		hostname_container, hostname = self.window.entry(_("Computer's name (e.g. johndesktop)"))
		
		# Set and hide
		if self.settings["userfullname"]:
			userfullname_container.hide()
			userfullname.set_text(self.settings["userfullname"])
		if self.settings["username"]:
			username_container.hide()
			username.set_text(self.settings["username"])
		if self.settings["password"]:
			password1_container.hide()
			password2_container.hide()
			password1.set_text(self.settings["password"])
			password2.set_text(self.settings["password"])
		if not self.settings["root"] == None:
			# We should at least handle root.
			if self.settings["root"]:
				# Is true, make the switch True.
				root_switch.set_active(True)
			if self.settings["rootpassword"]:
				# Set password and hide entries
				root_password1_container.hide()
				root_password2_container.hide()
				root_password1.set_text(self.settings["rootpassword"])
				root_password2.set_text(self.settings["rootpassword"])
		else:
			# Hide all
			root_switch_container.hide()
			root_password1_container.hide()
			root_password2_container.hide()
			verbose("Root disabled.")
		if self.settings["hostname"]:
			hostname_container.hide()
			hostname.set_text(self.settings["hostname"])
		
		# Connect.
		userfullname.connect("changed", self.on_userfullname_change)
		username.connect("changed", self.on_username_change)
		password1.connect("changed", self.on_password_change)
		password2.connect("changed", self.on_password_change)
		root_switch.connect("activate", self.on_rootswitch_change)
		root_password1.connect("changed", self.on_root_password_change)
		root_password2.connect("changed", self.on_root_password_change)
		hostname.connect("changed", self.on_hostname_change)
				
		gtk3.Gtk.main()
	
	def on_userfullname_change(self, obj):
		""" Handles userfullname change. """
		
		self.window.set_header("error", "LOL", "ASD")
	
	def on_username_change(self, obj):
		""" Handles username change. """
		
		pass
	
	def on_password_change(self, obj):
		""" Handles password change. """
		
		pass
	
	def on_rootswitch_change(self, obj, other):
		""" Handles rootswitch change. """
		
		pass
	
	def on_root_password_change(self, obj):
		""" Handles root password change. """
		
		pass
	
	def on_hostname_change(self, obj):
		""" Handles hostname change. """
		
		pass

#		if not self.settings["root"] == None:
#			if not self.settings["root"]:
#				res = self.window.switch(_("Do you want to enable root account?"), default=False)
#			else:
#				res = True
#			if res and not self.settings["rootpassword"]:
#				self.settings["rootpassword"] = self.password_prompt(_("root's password"))
#				self.settings["root"] = True
#				verbose("Selected root password.")
#			elif not res:
#				verbose("Root disabled.")
#			else:
#				verbose("preseeded root password.")
#			print
#		else:
#			root_switch_container.hide() # Hide root switch
#			root_password1_container.hide()
#			root_password2_container.hide() # Hide password entries
#			verbose("Root disabled.")

		
		
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
			warn(_("The password should be composed of at least six charchters."))
			return self.password_prompt(text)
		passw2 = self.entry(text + _(" (again)"), password=True)
		
		if not passw1 == passw2:
			# Wrong!
			warn(_("The passwords don't match! Please retry."))
			return self.password_prompt(text)
		else:
			return passw1
