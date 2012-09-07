# -*- coding: utf-8 -*-
# linstaller echo.partusb module install - (C) 2012 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.frontends.glade as glade
import t9n.library
_ = t9n.library.translation_init("linstaller")

class Bootloader(glade.Progress):
    def progress(self):
        """ Do the magic. """
        self.parent.progress_wait_for_quota()
        
        # PASS 1: INSTALL
        self.parent.progress_set_text(_("Installing bootloader..."))
    	self.parent.moduleclass.install()
        self.parent.progress_set_percentage(1)
		
class Frontend(glade.Frontend):
    def ready(self):
		""" Start the frontend """
		
		# Get a progressbar
		progress = self.set_header("hold", _("Installing bootloader..."), _("This may take a while."))
        self.progress_set_quota(1)
        
    def process(self):
        clss = Bootloader(self)
        clss.start()