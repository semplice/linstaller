# -*- coding: utf-8 -*-
# linstaller ubuntu module install - (C) 2012 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.module as module
import linstaller.core.main as m

import os, re, subprocess, shutil

import glob
from apt.cache import Cache

from linstaller.core.main import warn,info,verbose

# NOTE: This is a ubuntu-specific module.

# FIXME (SORTA OF): We are getting cache outside of chroot, using rootdir. We really should do something inside chroot.
cache = Cache(rootdir="/linstaller/target") ## HUGE FIXME!!! Needs to take setting from main_settings["target"]!!

class Install(module.Install):
	def run_hooks(self, path, *args):
		for hook in glob.iglob(path):
			if not os.access(hook[1:], os.X_OK):
				continue
			m.sexec("%(hook)s %(args)s" % {"hook":hook,"args":" ".join(args)})

	def configure_python(self):
		"""Byte-compile Python modules.

		To save space, Ubuntu excludes .pyc files from the live filesystem.
		Recreate them now to restore the appearance of a system installed
		from .debs.
		
		This is taken from ubiquity (ubuntu desktop installer) sources."""
				
		# Python standard library.
		re_minimal = re.compile('^python\d+\.\d+-minimal$')
		python_installed = sorted(
			[pkg[:-8] for pkg in cache.keys()
					  if re_minimal.match(pkg) and cache[pkg].is_installed])
		
		for python in python_installed:
			re_file = re.compile('^/usr/lib/%s/.*\.py$' % python)
			to_recompile = []
			
			for pkg in (cache["%s-minimal" % python], cache["python"]):
				for f in pkg.installed_files:
					if re_file.match(f) and not os.path.exists("%sc" % f): to_recompile.append(f)
			
			m.sexec("%(python)s /usr/lib/%(python)s/py_compile.py %(files)s" % {"python":python, "files":" ".join(to_recompile)})
		
		 
		# Modules provided by the core Debian Python packages.
		default = subprocess.Popen(
			['pyversions', '-d'],
			stdout=subprocess.PIPE).communicate()[0].rstrip('\n')
		if default:
			m.sexec("%s -m compileall /usr/share/python/" % default)
		if os.path.exists("/usr/bin/py3compile"):
			m.sexec("py3compile -p python3 /usr/share/python3")

		# Public and private modules provided by other packages.
		if os.path.exists("/usr/bin/pyversions"):
			supported = subprocess.Popen(
				['pyversions', '-s'],
				stdout=subprocess.PIPE).communicate()[0].rstrip('\n')
			for python in supported.split():
				try:
					cachedpython = cache['%s-minimal' % python]
				except KeyError:
					continue
				if not cachedpython.is_installed:
					continue
				version = cachedpython.installed.version
				self.run_hooks('/usr/share/python/runtime.d/*.rtinstall',
						  'rtinstall', python, '', version)
				self.run_hooks('/usr/share/python/runtime.d/*.rtupdate',
						  'pre-rtupdate', python, python)
				self.run_hooks('/usr/share/python/runtime.d/*.rtupdate',
						  'rtupdate', python, python)
				self.run_hooks('/usr/share/python/runtime.d/*.rtupdate',
						  'post-rtupdate', python, python)

		if os.path.exists("/usr/bin/py3versions"):
			supported = subprocess.Popen(
				['py3versions', '-s'],
				stdout=subprocess.PIPE).communicate()[0].rstrip('\n')
			for python in supported.split():
				try:
					cachedpython = cache['%s-minimal' % python]
				except KeyError:
					continue
				if not cachedpython.is_installed:
					continue
				version = cachedpython.installed.version
				self.run_hooks('/usr/share/python3/runtime.d/*.rtinstall',
						  'rtinstall', python, '', version)
				self.run_hooks('/usr/share/python3/runtime.d/*.rtupdate',
						  'pre-rtupdate', python, python)
				self.run_hooks('/usr/share/python3/runtime.d/*.rtupdate',
						  'rtupdate', python, python)
				self.run_hooks('/usr/share/python3/runtime.d/*.rtupdate',
						  'post-rtupdate', python, python)

	def set_kernel(self):
		""" Final set-up of the kernel """
		
		# Get the kernel package installed
		kernel_package = False
		re_minimal = re.compile('^linux-image-\d+\.\d+\.\d+\-\d+-.*$')
		for pkg in cache.keys():
			if re_minimal.match(pkg) and cache[pkg].is_installed:
				kernel_package = pkg
				break
		
		if not kernel_package: raise m.UserError("Unable to determine the correct kernel.")
		
		# Rename the generic vmlinuz that we previously copied to /boot
		version = kernel_package.replace("linux-image-","")
		shutil.move("/boot/vmlinuz", "/boot/vmlinuz-%s" % version)
		
		# Update initramfs
		m.sexec("update-initramfs -c -k %s" % version)
		

class Module(module.Module):
	def start(self):
		""" Start module """
		
		# Due to a limitation/simplification of linstaller's chroot capabilites, we can't copy the kernel after declaring the Install class.
		# Copy that now.
		verbose("Copying kernel...")
		self.copy_kernel()
		
		self.install = Install(self)
		
		module.Module.start(self)
	
	def copy_kernel(self):
		""" Copies the ubuntu kernel from the image to /boot.
		Needs to be executed outside chroot (that's why it's not in Install). """
		
		shutil.copy2(self.settings["kernel"], os.path.join(self.main_settings["target"], "boot/vmlinuz"))
	
	def seedpre(self):
		""" Caches variables used in this module. """
		
		self.cache("kernel","/cdrom/casper/vmlinuz.efi")
