# -*- coding: utf-8 -*-
# linstaller userhost module install - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.cli_frontend as cli
import linstaller.core.module as module
import linstaller.core.main as m
import t9n.library
_ = t9n.library.translation_init("linstaller")

import linstaller.core.libmodules.chroot.library as lib

from linstaller.core.main import warn,info,verbose

import os, sys

import debconf

# NOTE: This is a Debian-specific module. 'user-setup' is available only on Debian(-based) distributions!

class Install(module.Install):
	def user_set(self):
		""" Sets into the debconf database user-setup relevant settings. """
	
		db = debconf.DebconfCommunicator("linstaller")
						
		# Get relevant settings...
		userfullname = self.moduleclass.modules_settings["userhost"]["userfullname"]
		username = self.moduleclass.modules_settings["userhost"]["username"]
		password = self.moduleclass.modules_settings["userhost"]["password"]
		root = self.moduleclass.modules_settings["userhost"]["root"]
		if root == "True":
			# get root password
			rootpassword = self.moduleclass.modules_settings["userhost"]["rootpassword"]
		
		# Now, set
		
		db.set("passwd/user-fullname", userfullname)
		db.set("passwd/username", username)
		db.set("passwd/user-password", password)
		# Enable root?
		if root == "True":
			db.set("passwd/root-login", "true")
			db.set("passwd/root-password", rootpassword)
		else:
			db.set("passwd/root-login", "false")

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


class CLIFrontend(cli.CLIFrontend):
	def start(self):
		""" Start the frontend """

		# Get a progressbar
		progress = self.progressbar(_("Creating user:"), 3)
		
		try:
			verbose("Creating user")
			# USER: set.
			self.moduleclass.install.user_set()
			progress.update(1)
			
			# USER: commit.
			self.moduleclass.install.user_commit()
			progress.update(2)
			
			verbose("Setting username")
			# HOSTNAME: commit
			self.moduleclass.install.host_commit()
			progress.update(3)
		finally:
			# Exit
			self.moduleclass.install.close()
		
		progress.finish()


class Module(module.Module):
	def start(self):
		""" Start module """
		
		self.install = Install(self)
		
		module.Module.start(self)

	def _associate_(self):
		""" Associate frontends. """
		
		self._frontends = {"cli":CLIFrontend}
