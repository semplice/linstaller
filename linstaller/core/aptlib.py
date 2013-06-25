# -*- coding: utf-8 -*-
# linstaller core apt library - (C) 2013 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.main as m

import apt.cache
import os

RepositoryType = m.enum("TRIVIAL", "AUTOMATIC")

class Cache(apt.cache.Cache):
	
	""" This class is intended to manage packages and repositories in target, 
	outside the chroot. """
	
	def __init__(self, rootdir="/linstaller/target", memonly=True, sourceslist="/tmp/linstaller_sourceslist.list"):
		
		# Just one catch: we need to specify rootdir as libraries cannot
		# access the main_settings dictionary.
		# The calling module should set rootdir to self.main_settings["target"].
		
		apt.cache.Cache.__init__(self, progress=None, rootdir=rootdir, memonly=memonly)
		
		self.sourceslist = sourceslist
		if os.path.exists(self.sourceslist):
			os.remove(self.sourceslist)
	
	def add_repository(self, mode, path, binarydir="./", distro=None, sections=None, withsrc=False):
		""" Adds the repository to self.sourceslist.
		
		path is the URI of the repository.
		
		mode is the relevant repository type (see RepositoryType enum)
		
		If mode is RepositoryType.TRIVIAL, binarydir is the only addition parameter (defaults to ./) 
		
		If mode is RepositoryType.AUTOMATIC, the additional - and required - parameters are distro and 
		sections (tuple), while withsrc is the only additional parameter. If True, it will set deb-src
		repositories too. """
		
		if os.path.exists(self.sourceslist):
			openmode = "a"
		else:
			openmode = "w"
		
		if mode == RepositoryType.TRIVIAL:
			with open(self.sourceslist, openmode) as f:
				f.write("deb %(path)s %(binarydir)s\n" % {"path":path, "binarydir":binarydir})
		elif mode == RepositoryType.AUTOMATIC:
			if None in (distro, sections):
				raise TypeError("add_repository() in RepositoryType.AUTOMATIC mode needs distro and sections defined")
			
			with open(self.sourceslist, openmode) as f:
				f.write("deb %(path)s %(distro)s %(sections)s\n" % {"path":path, "distro":distro, "sections":" ".join(sections)})
				if withsrc:
					f.write("deb-src %(path)s %(distro)s %(sections)s\n" % {"path":path, "distro":distro, "sections":" ".join(sections)})
	
	def update(self, fetch_progress=None, pulse_interval=0, raise_on_error=True):
		""" Run the equivalent of apt-get update.
		
		See apt.cache.update() for a detailed explanation.
		This method will call update() with the sources_list overrided by self.sourceslist. """
		
		apt.cache.Cache.update(self,
			fetch_progress=fetch_progress,
			pulse_interval=pulse_interval,
			raise_on_error=raise_on_error,
			sources_list=self.sourceslist
		)
