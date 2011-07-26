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
from liblaiv_setup import TimeZone
# Start timezone class
tz = TimeZone()

class CLIFrontend(cli.CLIFrontend):
	def start(self):
		""" Start the frontend """
		
		self.header(_("Timezone selection"))
		
		# Get the current timezone...
		if not self.settings["timezone"]:
			timezone = tz.get_current_timezone()
			print _("Default timezone is:")
			print
			print ("  %s" % timezone)
			print
			res = self.question(_("Do you want to change it?"), default=True)
			if res:
				# We should change it...
				timezone = self.select_timezone()
		
			# Write to self.settings
			self.settings["timezone"] = timezone
		
		verbose("Selected timezone %s" % self.settings["timezone"])
	
	def select_timezone(self):
		""" Timezone selection """

		self.header(_("Select the region where you live"))
		reg, rreg, tim = tz.list()

		# Print regions
		for num, name in reg.iteritems():
			print "%d: %s" % (num, name)

		try:
			rchoice = int(self.entry(_("Insert your choice")))
		except:
			return self.select_timezone()

		if not rchoice in reg:
			warn(_("Unknown region."))
			return self.select_timezone()

		self.header(_("Select city"))
		
		# Display cities
		num = 0
		listed = {}
		for name in tim:
			if tim[name] == rchoice:
				print "%d: %s" % (num, name)
				listed[num] = name
				num += 1

		try:
			choice = int(self.entry(_("Insert your choice")))
		except:
			return self.select_timezone()
		if not choice in listed:
			warn(_("Unknown zone."))
			return self.select_timezone()
		return tz.join(reg[rchoice], listed[choice])

class Module(module.Module):
	def _associate_(self):
		""" Associate frontends. """
		
		self._frontends = {"cli":CLIFrontend}
	
	def seedpre(self):
		""" Caches variables used by this module. """
		
		self.cache("timezone")
