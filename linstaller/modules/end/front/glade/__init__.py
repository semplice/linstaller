# -*- coding: utf-8 -*-
# linstaller inst_test module install - (C) 2012 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.frontends.glade as glade
import linstaller.core.main as m
import t9n.library
_ = t9n.library.translation_init("linstaller")

from linstaller.core.main import warn,info,verbose
		
class Frontend(glade.Frontend):
	def ready(self):
		""" Ready! (to wait...) """

		self.set_header("ok", _("Already finished?"), _("It seems so."))