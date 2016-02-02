# -*- coding: utf-8 -*-
# linstaller userhost module install - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.module as module

import linstaller.core.main as m

import os, sys

# NOTE: This is a Debian-specific module. 'user-setup' is available only on Debian(-based) distributions!

class Install(module.Install):
	def user_set(self):
		""" Sets into the debconf database user-setup relevant settings. """

		import debconf # Import debconf now, this will improve hopefully 'nolive'-capable distributions list

		db = debconf.DebconfCommunicator("linstaller")
						
		# Get relevant settings...
		userfullname = self.moduleclass.modules_settings["userhost"]["userfullname"]
		username = self.moduleclass.modules_settings["userhost"]["username"]
		password = self.moduleclass.modules_settings["userhost"]["password"]
		root = self.moduleclass.modules_settings["userhost"]["root"]
		if root:
			# get root password
			rootpassword = self.moduleclass.modules_settings["userhost"]["rootpassword"]
		
		# Now, set
		
		db.set("passwd/user-fullname", userfullname)
		db.set("passwd/username", username)
		db.set("passwd/user-password", password)
		# Enable root?
		if root:
			db.set("passwd/root-login", "true")
			db.set("passwd/root-password", rootpassword)
		else:
			db.set("passwd/root-login", "false")
			
			# Groups
			db.set("passwd/user-default-groups",
				self.moduleclass.settings["user_default_groups"]
				+ " %s" % self.moduleclass.settings["user_additional_groups"]
				if self.moduleclass.settings["user_additional_groups"]
				else ""
			)

		# Make sure we make the user
		db.set("passwd/make-user", "true")
		
		# User's UID
		db.set("passwd/user-uid", "1000")
		
		db.shutdown() # Exit.
	
	def user_commit(self):
		""" Creates the user. """
		
		# Create and chmod /etc/passwd- (temporary workaround)
		asd = open("/etc/passwd-","w")
		asd.close()
		os.chmod("/etc/passwd-",0600)
		
		# Ok... now invoking user-setup to make the changes we defined before...
		m.sexec("/usr/lib/user-setup/user-setup-apply")
	
	def host_commit(self):
		""" Gets and sets the hostname. """
		
		hostname = self.moduleclass.modules_settings["userhost"]["hostname"]
		
		# /etc/hostname
		with open("/etc/hostname","w") as f:
			f.write(hostname + "\n")
		
		# /etc/hosts
		with open("/etc/hosts","w") as f:
			f.write("""127.0.0.1 localhost localhost.localdomain %s

::1 localhost.localdomain localhost

# The following lines are desirable for IPv6 capable hosts
::1     ip6-localhost ip6-loopback
fe00::0 ip6-localnet
ff00::0 ip6-mcastprefix
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
ff02::3 ip6-allhosts
""" % (hostname))


class Module(module.Module):
	def start(self):
		""" Start module """
		
		self.install = Install(self)
		
		module.Module.start(self)
	
	def seedpre(self):
		"""
		Cache settings.
		"""
		
		self.cache("user_default_groups", " ".join([
			"audio",
			"cdrom",
			"dip",
			"floppy",
			"video",
			"plugdev",
			"netdev",
			"powerdev",
			"scanner",
			"bluetooth",
			"dialout",
			"fax",
			"tape",
			"fuse",
			"lpadmin"
		]))
		
		self.cache("user_additional_groups")

