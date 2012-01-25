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
		
		# Set the steps
		self.steps = ["userfullname", "username", "password", "hostname"]
				
		self.window.set_header("info", _("Users & Hostname"), _("Set users and hostname"))
		
		# Initial user
		self.userfullname_container, self.userfullname = self.window.entry(_("New user's full name (e.g. John Doe)"))
		self.username_container, self.username = self.window.entry(_("%s's username (no spaces; e.g: john)") % self.settings["userfullname"])
		self.window.text_new()
		
		# Passwords
		password1, password2 = self.window.password_entry_with_confirm(_("%s's password") % self.settings["userfullname"])
		self.window.text_new()
		
		self.password1_container, self.password1 = password1
		self.password2_container, self.password2 = password2
		
		# Root
		self.root_switch_container, self.root_switch = self.window.switch(_("Do you want to enable root account?"), default=False)
		root_password1, root_password2 = self.window.password_entry_with_confirm(_("root's password"))
		
		self.root_password1_container, self.root_password1 = root_password1 # Split the confirms
		self.root_password2_container, self.root_password2 = root_password2 # Same.

		# Hostname
		self.hostname_container, self.hostname = self.window.entry(_("Computer's name (e.g. johndesktop)"))
		
		# Set and hide
		if self.settings["userfullname"]:
			self.userfullname_container.hide()
			self.userfullname.set_text(self.settings["userfullname"])
		if self.settings["username"]:
			self.username_container.hide()
			self.username.set_text(self.settings["username"])
		if self.settings["password"]:
			self.password1_container.hide()
			self.password2_container.hide()
			self.password1.set_text(self.settings["password"])
			self.password2.set_text(self.settings["password"])
		if not self.settings["root"] == None:
			# We should at least handle root.
			if self.settings["root"]:
				# Is true, make the switch True.
				self.root_switch.set_active(True)
			else:
				# False, make the switch False and hide
				self.root_switch.set_active(False)
				self.root_password1_container.hide()
				self.root_password2_container.hide()

			if self.settings["rootpassword"]:
				# Set password and hide entries
				self.root_password1_container.hide()
				self.root_password2_container.hide()
				self.root_password1.set_text(self.settings["rootpassword"])
				self.root_password2.set_text(self.settings["rootpassword"])
		else:
			# Hide all
			self.root_switch_container.hide()
			self.root_password1_container.hide()
			self.root_password2_container.hide()
			verbose("Root disabled.")
		if self.settings["hostname"]:
			self.hostname_container.hide()
			self.hostname.set_text(self.settings["hostname"])
		
		# Connect.
		self.userfullname.connect("changed", self.on_userfullname_change)
		self.username.connect("changed", self.on_username_change)
		self.password1.connect("changed", self.on_password_change)
		self.password2.connect("changed", self.on_password_change)
		self.root_switch.connect("notify::active", self.on_rootswitch_change)
		self.root_password1.connect("changed", self.on_root_password_change)
		self.root_password2.connect("changed", self.on_root_password_change)
		self.hostname.connect("changed", self.on_hostname_change)
				
		gtk3.Gtk.main()
		
	def on_userfullname_change(self, obj):
		""" Handles userfullname change. """
				
		if obj.get_text():
			self.step_complete("userfullname")
		else:
			self.step_incomplete("userfullname")

		self.error_remove("userfullname")
		
		self.error_check()

	def on_username_change(self, obj):
		""" Handles username change. """
				
		# Check username
		check = self.invalid("username", obj.get_text())
		if check:
			# Something wrong
			self.error_add("username", _("You can't use %s in the username") % str(check))
		else:
			self.error_remove("username")

			if obj.get_text():
				self.step_complete("username")
			else:
				self.step_incomplete("username")

		self.error_check()

	def password_check(self, passw1, passw2):
		""" Returns True if the password match, False if not and None if it not has the minimal required chars. """
		
		if len(passw1) < int(self.settings["password_min_chars"]):
			return None
		
		if not passw1 == passw2:
			# Wrong!
			return False
		else:
			return True

	def on_password_change(self, obj):
		""" Handles password change. """
		
		check = self.password_check(self.password1.get_text(), self.password2.get_text())
		if check == None:
			self.error_add("password", _("The password should be composed of at least %s charchters.") % self.settings["password_min_chars"])
		elif check == False:
			self.error_add("password", _("The passwords doesn't match! Please retry."))
		else:
			self.error_remove("password")

			if obj.get_text():
				self.step_complete("password")
			else:
				self.step_incomplete("password")

		self.error_check()
	
	def on_rootswitch_change(self, obj, other):
		""" Handles rootswitch change. """
				
		if obj.get_active():
			# Show entries
			self.steps.append("root_password")
			
			self.root_password1_container.show()
			self.root_password2_container.show()
		else:
			if "root_password" in self.steps: self.steps.remove("root_password")
			if "root_password" in self.completed_steps: self.completed_steps.remove("root_password")
			self.error_remove("root_password")
			
			self.root_password1_container.hide()
			self.root_password2_container.hide()
		
		self.error_check()
	
	def on_root_password_change(self, obj):
		""" Handles root password change. """
		
		check = self.password_check(self.root_password1.get_text(), self.root_password2.get_text())
		if check == None:
			self.error_add("root_password", _("The root password should be composed of at least %s charchters.") % self.settings["password_min_chars"])
		elif check == False:
			self.error_add("root_password", _("The root passwords doesn't match! Please retry."))
		else:
			self.error_remove("root_password")

			if obj.get_text():
				self.step_complete("root_password")
			else:
				self.step_incomplete("root_password")

		self.error_check()
	
	def on_hostname_change(self, obj):
		""" Handles hostname change. """
		
		# Check hostname
		check = self.invalid("hostname", obj.get_text())
		if check:
			# Something wrong
			self.error_add("hostname", _("You can't use %s in the hostname") % str(check))
		else:
			if obj.get_text():
				self.step_complete("hostname")
			else:
				self.step_incomplete("hostname")

			self.error_remove("hostname")

		self.error_check()
			
	def invalid(self, what, text):
		""" Checks if a hostname/username is valid. """
		
		if what == "hostname":
			ALLOWED_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.-"
		else:
			ALLOWED_CHARS = "abcdefghijklmnopqrstuvwxyz0123456789.-"
		
		unallowed = []
		for lettera in text:
			if lettera not in ALLOWED_CHARS:
				unallowed += lettera

		if unallowed:
			return unallowed
		else:
			return False
