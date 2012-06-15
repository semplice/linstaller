# -*- coding: utf-8 -*-
# linstaller sample service - (C) 2012 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a service of linstaller, should not be executed as a standalone application.

import linstaller.core.service
import linstaller.core.main as m

from linstaller.core.main import info, warn, verbose

import time

class Service(linstaller.core.service.Service):
	def ready(self):
		info("Sample service called!")
	
	def on_module_change(self):
		info("Module changed to %s" % self.current_module)
	
	def on_frontend_change(self):
		info("Frontend changed to %s" % self.current_frontend)
