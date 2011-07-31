# -*- coding: utf-8 -*-
# linstaller language module frontend - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.cli_frontend as cli
import linstaller.core.main as m
import linstaller.core.module as module
import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import warn,info,verbose
from liblaiv_setup import Language, Keyboard
la = Language()
ke = Keyboard()

class CLIFrontend(cli.CLIFrontend):
	def start(self):
		""" Start the frontend """
		
		self.header(_("Language & Keyboard selection"))
		
		if not self.settings["ask"] == "False":
			verbose("Asking for language and keyboard.")
			# If ask is "False", do not ask at all, instead using system's language and keyboard
			
			if not self.settings["language"]:
				locale = self.entry(_("Please insert your locale here (e.g. it, or it_IT, or it_IT.UTF-8)"))
				# Check if the locale is good...
				result = la.detect_best_locale(locale)
				if result == 1:
					# Something wrong... restart
					_null = self.entry(_("Unknown locale. [press ENTER to continue]"), blank=True)
					return "restart"
				
				# Preseed.
				self.settings["language"] = result
			else:
				best = la.detect_best_locale(self.settings["language"])
				if best == 1:
					# Wrong locale. fallback to en_us.UTF8
					best = "en_US.UTF-8"
				self.settings["language"] = best
						
			# Keyboard
			if not self.settings["keyboard"]:
				keyboard = self.entry(_("Please insert your keyboard layout (e.g: it; or it,pc105)"))
				# FIXME: laiv-setup: should verify
			else:
				keyboard = self.settings["keyboard"] # Get keyboard from preseed.
				
			# Split.
			if len(keyboard.split(",")) == 1:
				# Only keyboard specified.
				self.settings["_model"] = False
				self.settings["keyboard"] = keyboard
			else:
				# Keyboard and model.
				keyboard = keyboard.split(",")
				self.settings["keyboard"] = keyboard[0]
				self.settings["_model"] = keyboard[1]
		else:
			# Do not ask; instead using host's language and keyboard layout.
			self.settings["language"] = la.get_current_locale()
			layout, model = ke.get_current_layout_and_model()
			self.settings["keyboard"] = layout
			self.settings["_model"] = model

		verbose("Selected language: %s" % self.settings["language"])
		verbose("Selected keyboard: %s (model %s)" % (self.settings["keyboard"], self.settings["_model"]))


class Module(module.Module):
	def _associate_(self):
		""" Associate frontends. """
		
		self._frontends = {"cli":CLIFrontend}
	
	def seedpre(self):
		""" Caches variables used by this module. """
		
		self.cache("ask")
		self.cache("language")
		self.cache("keyboard")
		
		## INTERNAL
		self.cache("_model")
