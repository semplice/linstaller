# -*- coding: utf-8 -*-
# linstaller welcome module frontend - (C) 2011-12 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.frontends.glade as glade
import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import warn,info,verbose,root_check		

class Frontend(glade.Frontend):
	def ready(self):
		
		# Initiate steps
		self.steps_init()
		self.steps_set_index(index={"userfullname":_("The user full name"), "username":_("The username"), "userpassword":_("The user password"), "hostname":_("The computer name")})
		
		# get objects
		self.userfullname_t = self.objects["builder"].get_object("userfullname_t")
		self.userfullname = self.objects["builder"].get_object("userfullname")
		self.userfullname.connect("changed", self.on_userfullname_change)
		
		self.username_t = self.objects["builder"].get_object("username_t")
		self.username = self.objects["builder"].get_object("username")
		self.username.connect("changed", self.on_username_change)
		
		self.userpassword_t = self.objects["builder"].get_object("userpassword_t")
		self.userpassword = self.objects["builder"].get_object("userpassword")
		self.userpassword.connect("changed", self.on_userpassword_change)
		
		self.userpassword_confirm_t = self.objects["builder"].get_object("userpassword_confirm_t")
		self.userpassword_confirm = self.objects["builder"].get_object("userpassword_confirm")
		self.userpassword_confirm.connect("changed", self.on_userpassword_change)
		
		self.user_frame = self.objects["builder"].get_object("user_frame")
		
		self.root_expander = self.objects["builder"].get_object("root_expander")
		
		self.enableroot = self.objects["builder"].get_object("enableroot")
		self.enableroot.connect("notify::active", self.on_enableroot_change)
		
		self.rootpassword_frame = self.objects["builder"].get_object("rootpassword_frame")
		
		self.rootpassword_t = self.objects["builder"].get_object("rootpassword_t")
		self.rootpassword = self.objects["builder"].get_object("rootpassword")
		self.rootpassword.connect("changed", self.on_rootpassword_change)
		
		self.rootpassword_confirm_t = self.objects["builder"].get_object("rootpassword_confirm_t")
		self.rootpassword_confirm = self.objects["builder"].get_object("rootpassword_confirm")
		self.rootpassword_confirm.connect("changed", self.on_rootpassword_change)
		
		self.hostname_t = self.objects["builder"].get_object("hostname_t")
		self.hostname = self.objects["builder"].get_object("hostname")
		self.hostname.connect("changed", self.on_hostname_change)
		
		# Users
		if self.settings["userfullname"]:
			# Hide userfullname
			self.userfullname_t.hide()
			self.userfullname.hide()
		if self.settings["username"]:
			# Hide username
			self.username_t.hide()
			self.username.hide()
				
		# Passwords
		if  self.settings["password"]:
			# Hide password and pasword confirm
			self.userpassword_t.hide()
			self.userpassword.hide()
			self.userpassword_confirm_t.hide()
			self.userpassword_confirm.hide()
	
		# Hostname
		if self.settings["hostname"]:
			self.hostname_t.hide()
			self.hostname.hide()
				
		# Root
		if self.settings["root"] == None:
			# Disable everything root-related
			self.root_expander.hide()
		else:
			# See if we should hide the rootpassword fields (if preseeded)
			# We should mark root as enabled?
			if self.settings["root"] == False:
				# No.
				self.enableroot.set_active(False)
				# Fire up on_enableroot_change, for some reason is not fired
				self.on_enableroot_change(self.enableroot)
			else:
				# Yes.
				self.enableroot.set_active(True)
				# Fire up on_enableroot_change, for some reason is not fired
				self.on_enableroot_change(self.enableroot)
			if self.settings["rootpassword"]:
				# Hide password frame
				self.rootpassword_frame.hide()
				
				# Make the root switch unsensitive
				self.enableroot.set_sensitive(False)
			elif self.settings["root"] == True:
				# Ensure the expander is opened
				self.root_expander.set_expanded(True)
		
		# Do *ALL* checks
		self.on_userfullname_change(self.userfullname)
		self.on_username_change(self.username)
		self.on_userpassword_change(self.userpassword)
		self.on_hostname_change(self.hostname)
		
		# if virgin, set header
		if self.is_module_virgin:
			self.set_header("info", _("Users & Hostname"), _("Set users and hostname"))

		
		# Determine if we should hide the main frame and/or go directly to the next module
		if self.settings["userfullname"] and self.settings["username"] and self.settings["password"] and self.settings["hostname"]:
			self.user_frame.hide()
			
			if self.settings["root"] == None or (self.settings["root"] != None and self.settings["rootpassword"]):
				self.module_casper()

	def on_switching_module(self):
		""" Override on_switching_module. """
		
		self.root_expander.set_expanded(False)
			
	def on_userfullname_change(self, obj):
		""" Called when userfullname is changed. """
				
		if obj.get_text():
			self.steps_completed("userfullname")
			self.change_entry_status(obj, "ok")
		else:
			self.steps_uncompleted("userfullname")
			self.change_entry_status(obj, "hold")
	
	def on_username_change(self, obj):
		""" Called when username is changed. """
		
		text = obj.get_text()
		if not text:
			self.steps_uncompleted("username")
			self.change_entry_status(obj, "hold")
		else:
			# Check
			result = self.moduleclass.check("username", text)
			if result == True:
				self.steps_completed("username")
				self.change_entry_status(obj, "ok")
			else:
				failmessage = _("The username must not contain these characters: %s") % ", ".join(result)
				self.steps_failed("username", failmessage)
				self.change_entry_status(obj, "error", failmessage)
	
	def on_userpassword_change(self, obj):
		""" Called when userpassword is changed. """
		
		# Get the passwords
		passw1 = self.userpassword.get_text()
		passw2 = self.userpassword_confirm.get_text()
		
		# Check
		if passw1:
			if passw1 == passw2:
				# They are the same!
				self.steps_completed("userpassword")
				self.change_entry_status(self.userpassword, "ok")
				self.change_entry_status(self.userpassword_confirm, "ok")
			else:
				# They doesn't match!
				failmessage = _("The user passwords doesn't match!")
				self.steps_failed("userpassword", failmessage)
				self.change_entry_status(self.userpassword, "error", failmessage)
				self.change_entry_status(self.userpassword_confirm, "error", failmessage)
		else:
			# Passw1 is empty, put on hold
			self.steps_uncompleted("userpassword")
			self.change_entry_status(self.userpassword, "hold")
			self.change_entry_status(self.userpassword_confirm, "hold")
	
	def on_rootpassword_change(self, obj):
		""" Called when userpassword is changed. """
		
		# Get the passwords
		passw1 = self.rootpassword.get_text()
		passw2 = self.rootpassword_confirm.get_text()
		
		# Check
		if passw1:
			if passw1 == passw2:
				# They are the same!
				self.steps_completed("rootpassword")
				self.change_entry_status(self.rootpassword, "ok")
				self.change_entry_status(self.rootpassword_confirm, "ok")
			else:
				# They doesn't match!
				failmessage = _("The root passwords doesn't match!")
				self.steps_failed("rootpassword", failmessage)
				self.change_entry_status(self.rootpassword, "error", failmessage)
				self.change_entry_status(self.rootpassword_confirm, "error", failmessage)
		else:
			# Passw1 is empty, put on hold
			self.steps_uncompleted("rootpassword")
			self.change_entry_status(self.rootpassword, "hold")
			self.change_entry_status(self.rootpassword_confirm, "hold")
	
	def on_hostname_change(self, obj):
		""" Called when hostname is changed. """
		
		text = obj.get_text()
		if not text:
			self.steps_uncompleted("hostname")
			self.change_entry_status(obj, "hold")
		else:
			# Check
			result = self.moduleclass.check("hostname", text)
			if result == True:
				self.steps_completed("hostname")
				self.change_entry_status(obj, "ok")
			else:
				failmessage = _("The hostname must not contain these characters: %s") % ", ".join(result)
				self.steps_failed("hostname", failmessage)
				self.change_entry_status(obj, "error")

	def on_enableroot_change(self, obj, state=None):
		""" Called when enableroot widget is changed. """
		
		print("setting root to... %s" % str(obj.get_active()))
		
		if obj.get_active() == True:
			# Set seed
			self.settings["root"] = True
			# Set sensitivity to password fields
			self.rootpassword_frame.set_sensitive(True)
			
			# Add the rootpassword step to the steps
			self.steps_add("rootpassword", _("The root password"))
			# Trigger change
			self.on_rootpassword_change(self.rootpassword)
		else:
			# Set seed
			self.settings["root"] = False
			# Unset sensitivity to password fields
			self.rootpassword_frame.set_sensitive(False)
			
			# Remove the rootpassword step from the steps
			self.steps_remove("rootpassword")
	
