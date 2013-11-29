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
	
	header_title = _("Installation finished")
	header_subtitle = _("Press Reboot to restart to the installed system.")
	header_icon = "gtk-ok"
	
	def ready(self):
		""" Ready! (to wait...) """

		main_notebook = self.objects["builder"].get_object("main_notebook")
		main_notebook.set_current_page(1)

		self.objects["parent"].change_next_button_to_reboot_button()
