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
		
		self.header(_("Timezone selection"))
		
		# Get the current timezone...
		if not self.settings["timezone"]:
			timezone = self.moduleclass.tz.default
			print _("Default timezone is:")
			print
			print ("  %s" % timezone)
			print
			res = self.question(_("Do you want to change it?"), default=True)
			if res:
				# We should change it...
				timezone = self.timezone_loop()
				if timezone == "_exit": timezone = None
		
			# Write to self.settings
			self.settings["timezone"] = timezone
		
		verbose("Selected timezone %s" % self.settings["timezone"])


	def timezone_loop(self):
		""" Displays an interactive list to select the proper timezone. """

		self.header(_("Select the region where you live"))

		cls = self.moduleclass.tz
		
		lst = {}
		num = 0
		for zone in cls.supported:
			num += 1
			print " %s) %s" % (num, zone)
			
			# Add to lst
			lst[num] = zone
		
		# Add specify and exit
		num += 1
		print " %s) %s" % (num, _("Specify"))
		lst[num] = "_specify"
		
		print
		
		# Prompt
		choice = self.entry(_("Please insert your choice"), onlyint=True)
		if not choice in lst:
			# Wrong!
			print "E: %s" % _("Wrong choice!")
			return self.timezone_loop()
		
		### Build cities list

		self.header(_("Select city"))

		zone = lst[choice]
		
		if zone == "_exit":
			return "_exit"
		elif zone == "_specify":
			choice = self.entry(_("Please specify the timezone")).split("/")
			if len(choice) == 1:
				# We assume is only the zone.
				if choice[0] in cls.supported:
					zone = choice[0]
				else:
					print "E: %s" % _("Invalid zone!")
					return self.timezone_loop()
			else:
				# Both zone and city
				if choice[0] in cls.supported and choice[1] in cls.supported[choice[0]]:				
					# ok!
					return "%s/%s" % (choice[0], choice[1])
				else:
					# :/
					print "E: %s" % _("Invalid zone or city!")
					return self.timezone_loop()
					
		
		lst = {}
		num = 0
		for city in cls.supported[zone]:
			num += 1
			print " %s) %s" % (num, city)
			
			# Add to lst
			lst[num] = city

		# Add specify and exit
		num += 1
		print " %s) %s" % (num, _("Specify"))
		lst[num] = "_specify"
		
		print

		# Prompt
		choice = self.entry(_("Please insert your choice"), onlyint=True)
		if not choice in lst:
			# Wrong!
			print "E: %s" % _("Wrong choice!")
			return self.timezone_loop()
		
		### Get city
		city = lst[choice]
		
		if city == "_exit":
			return "_exit"
		elif city == "_specify":
			choice = self.entry(_("Please specify the city"))
			if choice in cls.supported[zone]:
				city = choice
			else:
				print "E: %s" % _("Invalid city!")
				return self.timezone_loop()
		
		return "%s/%s" % (zone, city)
