# -*- coding: utf-8 -*-
# lvm library. - (C) 2013 Eugenio "g7" Paolantonio and the Semplice Team.
# All rights reserved. Work released under the GNU GPL license, version 3 or later.
#
# This is a module of linstaller, should not be executed as a standalone application.

import linstaller.core.main as m
import commands
import os

import parted as pa

#import lvm as lvm_library
#lvm = lvm_library.Liblvm() # Needed to get it to work on non-GIT version of pylvm2.

# FIXME?: This library may be a bit slow, but we may bear with it as it
# is just an installation program...

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
		
		self.isLVM = True
		
		self.name = name

		# Cache VG informations
		self.reload_infos()

	def reload_infos(self):
		"""Reloads LogicalVolume informations"""
		
		self.infos = {}
		
		for line in commands.getoutput("vgs --noheadings %s" % self.name).split("\n"):
			if not line.replace(" ","").startswith("Filedescriptor"):
				# Example output:
				# testgroup   1   1   0 wz--n- 3,73g 1,73g
				line = line.split(" ")
				if len(line) == 1: continue # Skip blank lines
				# Remove blank items
				while line.count('') > 0:
					line.remove('')
				if not line[0] == self.name: continue
				
				print line
				
				# size
				self.infos["size"] = float(line[5].replace(",",".").replace("g",""))*1024.0
				
				# free
				self.infos["free"] = float(line[6].replace(",",".").replace("g",""))*1024.0

		if len(self.infos) == 0:
			# The volume does not exist!
			
			self.infos["exists"] = False
		else:
			self.infos["exists"] = True
	
	def getSize(self, unit="MB"):
		"""Returns the size in the unit specified."""
		
		if unit == "MB":
			return self.infos["size"]
		elif unit == "GB":
			return self.infos["size"]/1024.0
		
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
	
	@property
	def path(self):
		"""Returns the path of the Volume Group"""
		
		return os.path.join("/dev", self.name)
	
	@property
	def logicalvolumes(self):
		"""Returns a list with every logical volume contained in this group"""
		
		result = []
		
		for line in commands.getoutput("lvs --noheadings -o lv_name %s" % self.name).split("\n"):
			line = line.replace(" ","")
			
			if not line.startswith("Filedescriptor"):
				# Ensure we skip filedescriptors
				result.append(LogicalVolume(line, self))
				# Ensure we do not include fake "non-existant" volumes
				if result[-1].infos["exists"] == False: removed = result.pop()
		
		# Add too a freespace LogicalVolume
		if self.infos["free"] > 5: # Do not look at LVs under the 5 MB of size
			result.append(LogicalVolume(self.name + "-1", self))
		
		return result
	
	def getVolume(self, name):
		"""Returns the logical volume name if it is in this volume group"""

		for line in commands.getoutput("lvs --noheadings -o lv_name %s" % self.name).split("\n"):
			line = line.replace(" ","")
			
			if not line.startswith("Filedescriptor") and line == name:
				return LogicalVolume(line, self)

class LogicalVolume:
	def __init__(self, name, vgroup):
		"""A Logical Volume object.
		
		name is the name of the volume.
		vgroup is the volume group where the LV resiedes."""
		
		self.isLVM = True
		
		self.name = name
		self.vgroup = vgroup
		
		
		# FIXME: partdisks's glade frontend compatibility
		self.type = -1
		
		# Cache LV informations
		self.reload_infos()
	
	def reload_infos(self):
		"""Reloads LogicalVolume informations"""
		
		self.infos = {}
		
		for line in commands.getoutput("lvs --noheadings %s" % self.vgroup.name).split("\n"):
			if not line.replace(" ","").startswith("Filedescriptor"):
				# Example output:
				# testvolume testgroup -wi-a---- 2,00g
				line = line.split(" ")
				if len(line) == 1: continue # Skip blank lines
				# Remove blank items
				while line.count('') > 0:
					line.remove('')
				if not line[0] == self.name: continue
				
				print line
				
				# size
				self.infos["size"] = float(line[3].replace(",",".").replace("g",""))*1024.0

		if len(self.infos) == 0:
			# The volume does not exist!
			
			self.infos["exists"] = False
			self.partition = FakePartition(self)
		else:
			self.infos["exists"] = True
			try:
				## FIXME: The following does not work if the partition is empty! (no FS)
				self.partition = pa.Disk(device=pa.Device(self.path)).getFirstPartition()
			except:
				# If this is the case (see FIXME), do not crash on the user but instead
				# "disable" this LV...
				self.infos["exists"] = False
				self.partition = None
	
	def create(self, size):
		"""Creates the logical volume on self.vgroup with size 'size'."""
		
		m.sexec("lvcreate --name %(name)s --size %(size)s %(vgroup)s" % {"name":self.name, "size":size, "vgroup":self.vgroup.name})
		self.reload_infos()
	
	def rename(self, new):
		"""Renames the Logical Volume.
		
		new is the new volume's name."""
		
		m.sexec("lvrename %(vgroup)s %(name)s %(new)s" % {"vgroup":self.vgroup.name, "name":self.name, "new":new})
		self.name = new
		self.reload_infos()
	
	def remove(self):
		"""Removes the Logical Volume."""
		
		m.sexec("lvremove --force %s" % self.path)
		self.reload_infos()
	
	@property
	def path(self):
		"""Returns the path of the Logical Volume."""
		
		return os.path.join("/dev", self.vgroup.name, self.name)
	
	def getSize(self, unit="GB"):
		"""Returns the """
		
		pass

class FakePartition:
	"""FakePartition class to resemble a parted.Partition object on freespace LogicalVolumes."""
	
	def __init__(self, logicalvolume):
		
		self.logicalvolume = logicalvolume
		
		
		self.useLVM = True
		self.type = -1
		self.fileSystem = None
		self.number = -1 #freespace!
	
	def getSize(self, unit="GB"):
		
		if unit == "GB":
			return self.logicalvolume.vgroup.infos["free"]/1024.0
		elif unit == "MB":
			return self.logicalvolume.vgroup.infos["free"]

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
	
	Example output: {"testgroup":{"testvolume":LogicalVolume("testvolume", VolumeGroup("testgroup")}}"""
	
	result = {}
	
	for line in commands.getoutput("lvs --noheadings -o lv_name,vg_name").split("\n"):
		if not line.replace(" ","").startswith("Filedescriptor"):
			line = line.split(" ")
			# Remove blank items
			while line.count('') > 0:
				line.remove('')
			# Ensure we skip filedescriptors
			if not line[1] in result:
				# add the group dictionary
				result[line[1]] = {}
			result[line[1]][line[0]] = LogicalVolume(line[0], VolumeGroup(line[1]))
	
	# Add too a freespace LogicalVolume for every group
	for group, res in result.items():
		if VolumeGroups[group].infos["free"] > 5: # Do not look at LVs under the 5 MB of size
			result[group][group + "-1"] = LogicalVolume(group + "-1", VolumeGroups[group])
	
	return result 

def refresh():
	""" Refreshes the LVM objects lists... """
	
	PhysicalVolumes = return_pv()
	VolumeGroups = return_vg()
	LogicalVolumes = return_lv()
	
	global PhysicalVolumes, VolumeGroups, LogicalVolumes

refresh()
