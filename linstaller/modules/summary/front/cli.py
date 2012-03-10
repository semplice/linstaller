# -*- coding: utf-8 -*-
# linstaller summary module frontend - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.frontends.cli as cli
import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import warn,info,verbose,bold

class Frontend(cli.Frontend):
	def start(self):
		""" Start the frontend """
		
		self.header(_("Summary"))
				
		# Parse changed partitions
		print(_("These partitions will be used:") + "\n")
		changed = self.moduleclass.modules_settings["partdisks"]["changed"]
		for obj, value in changed.items():
			try:
				fs = value["obj"].fileSystem.type
				mountpoint = value["changes"]["useas"]
				
				# If /, tell the user that the distribution will be installed here
				if mountpoint == "/":
					text = ": " + bold(_("%(distroname)s will be installed here.") % {"distroname":self.moduleclass.main_settings["distro"]})
				else:
					text = ""
				
				print(_(" - %(part)s (%(filesystem)s, mounts on %(mountpoint)s)%(text)s") % {"part":obj, "filesystem":fs, "mountpoint":mountpoint, "text":text})
			except:
				verbose("Unable to print details for %s" % obj)
		
		#print(_("%(distroname)s will be installed in %(rootpartition)s.") % {"distroname":self.moduleclass.main_settings["distro"], "rootpartition":self.moduleclass.modules_settings["partdisks"]["root"]})
		#print(_("%(swappartition)s will be used as swap.") % {"swappartition":self.moduleclass.modules_settings["partdisks"]["swap"]})
		print
		
		# USB-Persistence
		try:
			size = self.moduleclass.modules_settings["echo.partusb"]["size"]
			print(_("The persistence partion will be of %s MB.") % size)
			print
		except:
			pass
		
		try:
			print(_("The default locale will be %(locale)s.") % {"locale":self.moduleclass.modules_settings["language"]["language"]})
		except:
			pass
		try:
			print(_("The default keyboard layout will be %(layout)s.") % {"layout":self.moduleclass.modules_settings["language"]["keyboard"]})
		except:
			pass
		print
		
		try:
			print(_("The main user will be %(userfullname)s (%(username)s).") % {"userfullname":self.moduleclass.modules_settings["userhost"]["userfullname"], "username":self.moduleclass.modules_settings["userhost"]["username"]})
			if self.moduleclass.modules_settings["userhost"]["root"]:
				# Root enabled
				print(_("Root account is enabled."))
			print(_("The computer hostname will be %(hostname)s.") % {"hostname":self.moduleclass.modules_settings["userhost"]["hostname"]})
		except:
			pass
		
		try:
			print(_("The machine will use this timezone: %(timezone)s.") % {"timezone":self.moduleclass.modules_settings["timezone"]["timezone"]})
		except:
			pass
		print
		
		try:
			print(_("The bootloader (%(bootloader)s) will be installed in %(bootloaderpath)s.") % {"bootloader":self.moduleclass.modules_settings["bootloader"]["bootloader"],"bootloaderpath":self.moduleclass.modules_settings["bootloader"]["device"]})
		except:
			pass
		print
				
		# We should continue?
		res = self.question(_("Do you really want to continue?"), default=True)
		if not res: self.end()
		
		verbose("Beginning installation.")
		
		self.header(_("Installing..."))
