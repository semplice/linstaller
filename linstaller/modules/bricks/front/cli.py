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

from libbricks.features import features, features_order

class Frontend(cli.Frontend):
	def start(self):
		""" Start the frontend """
		
		self.header(_("Feature selection"))
		
		self.settings["features"] = {}
		
		for feature in features_order:
			dic = features[feature]
			
			self.settings["features"][feature] = self.question("Enable %s?" % dic["title"], default=True)
