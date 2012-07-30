# -*- coding: utf-8 -*-
# linstaller language module frontend - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
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
		
		self.header(_("Language & Keyboard selection"))
		
		if self.settings["ask"]:
			verbose("Asking for language and keyboard.")
			# If ask is "False", do not ask at all, instead using system's language and keyboard
			
			if not self.settings["language"]:
				locale = self.entry(_("Please insert your locale here (e.g. it, or it_IT, or it_IT.UTF-8)"))
				# Check if the locale is good...
				result = self.moduleclass.la.get_best_locale(locale)
				if not result:
					# Something wrong... restart
					_null = self.entry(_("Unknown locale. [press ENTER to continue]"), blank=True)
					return "restart"
				
				# Preseed.
				self.settings["language"] = result
			else:
				best = self.moduleclass.la.get_best_locale(self.settings["language"])
				if not best:
					# Wrong locale. fallback to en_us.UTF8
					best = "en_US.UTF-8"
				self.settings["language"] = best
						
			# Keyboard
			if not self.settings["layout"]:
				self.settings["layout"] = self.entry(_("Please insert your keyboard layout (e.g: it)"))
				# FIXME: laiv-setup: should verify
			
			if not self.settings["model"]:
				self.settings["model"] = self.entry(_("Please insert your keyboard model (e.g: pc105, default is pc105)"), blank=True)
				if not self.settings["model"]: self.settings["model"] = "pc105"
				# FIXME: laiv-setup: should verify


			if not self.settings["variant"]:
				self.settings["variant"] = self.entry(_("Please insert your keyboard variant (press ENTER to skip)"), blank=True)
				if not self.settings["variant"]: self.settings["variant"] = None
				# FIXME: laiv-setup: should verify

		else:
			# Do not ask; instead using host's language and keyboard layout.
			self.settings["language"] = self.moduleclass.la.default
			self.settings["layout"] = self.moduleclass.ke.default_layout
			self.settings["model"] = self.moduleclass.ke.default_model
			self.settings["variant"] = self.moduleclass.ke.default_variant

		verbose("Selected language: %s" % self.settings["language"])
		verbose("Selected keyboard: %s (model %s, variant %s)" % (self.settings["layout"], self.settings["model"], self.settings["variant"]))
