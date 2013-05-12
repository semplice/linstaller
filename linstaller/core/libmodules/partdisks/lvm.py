# -*- coding: utf-8 -*-
# lvm library. - (C) 2011-12 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.main as m

import parted

import lvm as lvm_library
lvm = lvm_library.Liblvm() # Needed to get it to work on non-GIT version of pylvm2.

class PhysicalVolume:
	def __init__(self, disk=None, part=None):
		"""A Physical Volume object.
		
		It supports both entire disks or partitions (only one for object).
		
		disk is a parted.Disk object.
		part is a parted.Partition object."""
		
		if not disk and not part:
			raise m.CodeError("No phisical volume specified! (use disk= or part=)")
		elif disk and part:
			raise m.CodeError("Both disk and part specified! (use only one)")
		elif disk:
			self.pv = disk
		elif part:
			self.pv = part
	
	def initialize(self):
		"""Initalize the Phisical Volume."""
		
		if type(self.pv) == parted.Disk:
			# If we are initializing a disk, we need to erase the partition table
			# Using the good old dd to do so.
			m.sexec("dd if=/dev/zero of=%s bs=512 count=1" % self.pv.path)
		else:
			# We are initializing a partition, so we need to set the proper id
			print("FIXME: We need to set 0x8e to the partition!")
		
		# Our version is too old to have the pvCreate method.
		# We are fallbacking to the good old m.sexec
		m.sexec("pvcreate %s" % self.pv.path)
	
	
	
	
