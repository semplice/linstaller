# -*- coding: utf-8 -*-
# linstaller core apt library - (C) 2013 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.main as m

import apt_pkg
import apt
import shutil
import os

RepositoryType = m.enum("TRIVIAL", "AUTOMATIC")
MarkType = m.enum("INSTALL","DELETE","KEEP","UPGRADE")

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
		
		self.normal_source_list = apt_pkg.config.find("Dir::Etc::sourcelist")
		self.normal_source_dir = apt_pkg.config.find("Dir::Etc::sourceparts")
		self.normal_source_cleanup = apt_pkg.config.find("APT::List-Cleanup")
	
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
		
		# sources_list on update() seems to not work, let's workaround
		# with this
		apt_pkg.config.set("Dir::Etc::sourcelist", os.path.abspath(self.sourceslist))
		apt_pkg.config.set("Dir::Etc::sourceparts", "xxx")
		apt_pkg.config.set("APT::List-Cleanup", "0")
		
		self._list = apt_pkg.SourceList()
		self._list.read_main_list()
		
		return apt.cache.Cache.update(self,
			fetch_progress=fetch_progress,
			pulse_interval=pulse_interval,
			raise_on_error=raise_on_error,
			sources_list=None
		)
	
	def local_fetch(self, package):
		""" As fetch_archives() and apt.package.version.fetch_binary()
		do not download or are using symlinks, we are likely to fail
		because we will later enter the chroot and break the links.
		
		We need to actually copy the archive. This method uses shutil
		to accomplish that. """
		
		if package.is_installed:
			version = package.installed
		elif package.candidate:
			version = package.candidate
		else:
			version = pkg.versions[0]
		
		for uri in version.uris:
			if uri.startswith("file://"):
				uri = uri.replace("file://","")
				
				shutil.copy(uri, os.path.join(
					apt_pkg.config.find("Dir"),
					"var/cache/apt/archives")
				)
	
	def local_fetch_changes(self, changes=None):
		""" local_fetch()es only the packages marked "to install" in the
		changes list.
		
		If changes is None, the current cache's changes will be used."""
		
		if not changes: changes = self.get_changes()
		
		for pkg in changes:
			if pkg.marked_install:
				self.local_fetch(pkg)
	
	def change_rootdir(self, newrootdir):
		""" This method resets the rootdir to newrootdir.
		
		Unfortunately, apt.cache outside the chroot seems to commit
		to the host system even when rootdir has been defined.
		
		So this method comes handy to temporairly reset rootdir to /
		when the installer should work into the chroot and then to
		reset it to main_settings["target"]
		
		Keep in mind that this method does not re-read the APT
		configuration files again as the __init__() parent method
		seems to do when there is a rootdir specified. 
		
		open() needs to be called after this method, to avoid nasty
		problems. """

		if self._depcache:
			changes = self.get_changes()
		else:
			changes = ()
		
		# Save in a dictionary, as we can't get marks after open()
		saved = {}
		for pkg in changes:
			if pkg.marked_delete:
				saved[pkg.name] = MarkType.DELETE
			elif pkg.marked_install:
				saved[pkg.name] = MarkType.INSTALL
			elif pkg.marked_keep:
				saved[pkg.name] = MarkType.KEEP
			elif pkg.marked_upgrade:
				saved[pkg.name] = MarkType.UPGRADE		

		apt_pkg.config.set("Dir", newrootdir)
		apt_pkg.config.set("Dir::State::status", os.path.join(newrootdir, "var/lib/dpkg/status"))
		apt_pkg.config.set("Dir::bin::dpkg", os.path.join(newrootdir, "usr/bin/dpkg"))
		
		# Reset the sources.list to known values.
		apt_pkg.config.set("Dir::Etc::sourcelist", self.normal_source_list)
		apt_pkg.config.set("Dir::Etc::sourceparts", self.normal_source_dir)
		apt_pkg.config.set("APT::List-Cleanup", self.normal_source_cleanup)

		self._list = apt_pkg.SourceList()
		self._list.read_main_list()
		
		apt_pkg.init_system()

		self.open(progress=None)
		
		# Rebuild changes list
		for pkg, mark in saved.items():
			if mark == MarkType.DELETE:
				self[pkg].mark_delete()
			elif mark == MarkType.INSTALL:
				self[pkg].mark_install()
			elif mark == MarkType.KEEP:
				self[pkg].mark_keep()
			elif mark == MarkType.UPGRADE:
				self[pkg].mark_upgrade()
