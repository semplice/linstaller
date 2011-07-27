# -*- coding: utf-8 -*-
# unsquash library. - (C) 2011 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.main as m
import operator
import os
import time

from linstaller.core.main import info,warn,verbose

class Unsquash:
	def __init__(self, squashimage):
		
		# Set squashimage
		self.squashimage = squashimage
		self.TARGET = "/linstaller/target"
		
	def get_files(self):
		""" Get the number of files to be copied. """
		
		proc = m.execute("sleep 1; cat /tmp/foo", custom_log=m.subprocess.PIPE)
		#proc = m.execute("unsquashfs -d FROMHERE -l %s" % self.squashimage, custom_log=m.subprocess.PIPE, shell=False)
		# Start
		proc.start()
		
		# output...
		output = proc.process.communicate()[0].split("\n")
		
		return len(output)
	
	def begin(self):
		""" Unsquashes squashimage to TARGET """
		
		proc = m.execute("unsquashfs -d %(destination)s -f -i -fr 10 -da 10 -n %(image)s" % {"destination":self.TARGET, "image":self.squashimage}, custom_log=m.subprocess.PIPE)
		# Start
		proc.start()
		
		# Return object to frontend. It should parse it and launch progressbar.
		return proc
