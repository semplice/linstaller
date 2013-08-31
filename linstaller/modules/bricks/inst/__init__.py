# -*- coding: utf-8 -*-
# linstaller bricks module install - (C) 2013 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.module as module

class Install(module.Install):
	def run(self, InstallProgress):

		import libbricks.engine as engine

		atleastone = False

		for feature, choice in self.moduleclass.modules_settings["bricks"]["features"].items():
			
			status, packages, allpackages = engine.status(feature)
			
			if not choice:
				# remove!
				atleastone = True
				engine.remove(packages)
				
				# We should really, really, really ensure that no
				# dependency remains. We do this by marking too the
				# meta-package's dependencies as to be removed.
				
				for pkg in packages:
					pkgs = []
					for _pkg in engine.dependencies_loop_simplified(pkg):
						if _pkg in engine.cache and not _pkg.marked_delete:
							pkgs.append(_pkg)
					engine.remove(pkgs, auto=False)
		
		# Commit
		if atleastone:
			engine.cache.commit(install_progress=InstallProgress)

class Module(module.Module):
	def start(self):
		""" Start module. """

		# FIXME: supportrepo clashes with libbricks's apt.cache object.
		# This workaround fixes that.
		if "supportrepo.inst" in self.modules_settings and self.modules_settings["supportrepo.inst"]["cache"]:
			self.modules_settings["supportrepo.inst"]["cache"].change_rootdir("/")		

		self.install = Install(self)
		
		module.Module.start(self)
