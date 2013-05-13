# -*- coding: utf-8 -*-
# lvm library. - (C) 2013 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.main as m
import commands
import parted

#import lvm as lvm_library
#lvm = lvm_library.Liblvm() # Needed to get it to work on non-GIT version of pylvm2.

class PhysicalVolume:
	def __init__(self, device_name=None, disk=None, part=None):
		"""A Physical Volume object.
		
		It supports both entire disks or partitions (only one for object).
		
		device_name is a string with the path to the device.
		disk is a parted.Disk object.
		part is a parted.Partition object."""
		
		if not device_name and not disk and not part:
			raise m.CodeError("No phisical volume specified! (use device_name, disk= or part=)")
		elif (disk and part) or (device_name and disk) or (device_name and part):
			raise m.CodeError("Argument overload. See __init__ method documentation.")
		elif device_name:
			self.pv = device_name
		elif disk:
			self.pv = disk.path
		elif part:
			self.pv = part.path
	
	def create(self):
		"""Creates the Physical Volume."""
		
		if type(self.pv) == parted.Disk:
			# If we are initializing a disk, we need to erase the partition table
			# Using the good old dd to do so.
			m.sexec("dd if=/dev/zero of=%s bs=512 count=1" % self.pv)
		else:
			# We are initializing a partition, so we need to set the proper id
			print("FIXME: We need to set 0x8e to the partition!")
		
		# Our version is too old to have the pvCreate method.
		# We are fallbacking to the good old m.sexec
		m.sexec("pvcreate %s" % self.pv)
	
class VolumeGroup:
	def __init__(self, name):
		"""A Volume Group object.
		
		name is the name of the group."""
		
		self.name = name
	
	def create(self, devices):
		"""Creates the Volume Group.
		
		devices is a tuple which contains the list of devices to include into the VG."""
		
		if not type(devices) == tuple: devices = (devices,)
		
		_devices = []
		for device in devices:
			_devices.append(device.pv)
		
		m.sexec("vgcreate %(name)s %(devices)s" % {"name":self.name, "devices":" ".join(_devices)})
	
	def rename(self, new):
		"""Renames the Volume Group.
		
		new is the new group's name."""
		
		m.sexec("vgrename %(name)s %(new)s" % {"name":self.name, "new":new})
		self.name = new
	
	def remove(self):
		"""Removes the Volume Group."""
		
		m.sexec("vgremove %s" % self.name)

class LogicalVolume:
	def __init__(self, name, vgroup):
		"""A Logical Volume object.
		
		name is the name of the volume.
		vgroup is the volume group where the LV resiedes."""
		
		self.name = name
		self.vgroup = vgroup
	
	def create(self, size):
		"""Creates the logical volume on self.vgroup with size 'size'."""
		
		m.sexec("lvcreate --name %(name)s --size %(size)s %(vgroup)s" % {"name":self.name, "size":size, "vgroup":self.vgroup.name})
	
	def rename(self, new):
		"""Renames the Logical Volume.
		
		new is the new volume's name."""
		
		m.sexec("lvrename %(vgroup)s %(name)s %(new)s" % {"vgroup":self.vgroup.name, "name":self.name, "new":new})
		self.name = new
	
	def remove(self):
		"""Removes the Logical Volume."""
		
		m.sexec("lvremove %s" % os.path.join("/dev", self.vgroup.name, self.name))

def return_pv():
	"""Returns a dictionary with every PhyicalVolume present in the system.
	
	Example output: {"/dev/sdc1":PhysicalVolume(device_name="/dev/sdc1")}"""
	
	result = {}
	
	for line in commands.getoutput("pvs --noheadings -o pv_name").split("\n"):
		line = line.replace(" ","")
		
		if not line.startswith("Filedescriptor"):
			# Ensure we skip filedescriptors
			result[line] = PhysicalVolume(device_name=line)
	
	return result

def return_vg():
	"""Returns a dictionary with every VolumeGroup present in the system.
	
	Example output: {"testgroup":VolumeGroup("testgroup")}"""
	
	result = {}
	
	for line in commands.getoutput("vgs --noheadings -o vg_name").split("\n"):
		line = line.replace(" ","")
		
		if not line.startswith("Filedescriptor"):
			# Ensure we skip filedescriptors
			result[line] = VolumeGroup(line)
	
	return result

def return_lv():
	"""Returns a dictionary with every LogicalVolume present in the system.
	
	Example output: {"testvolume":LogicalVolume("testvolume", VolumeGroup("testgroup")}"""
	
	result = {}
	
	for line in commands.getoutput("lvs --noheadings -o lv_name,vg_name").split("\n"):
		if not line.replace(" ","").startswith("Filedescriptor"):
			line = line.split(" ")
			line.remove("")
			line.remove("")
			# Ensure we skip filedescriptors
			result[line[0]] = LogicalVolume(line[0], VolumeGroup(line[1]))
	
	return result 

PhysicalVolumes = return_pv()
VolumeGroups = return_vg()
LogicalVolumes = return_lv()
