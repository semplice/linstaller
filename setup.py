#!/usr/bin/env python
# linstaller setup (using distutils)
# Copyright (C) 2011 Eugenio "g7" Paolantonio. All rights reserved.
# Work released under the GNU GPL license, version 3.

from distutils.core import setup

setup(name='linstaller',
      version='2.11.0',
      description='Modular, preseedable, GNU/Linux distribution installer',
      author='Eugenio Paolantonio and the Semplice Team',
      author_email='me@medesimo.eu',
      url='http://launchpad.net/linstaller',
      scripts=['linstaller.py'],
      packages=["linstaller", "linstaller.core", "linstaller.frontends", "linstaller.core.libmodules",
      "linstaller.core.libmodules.chroot",
      "linstaller.core.libmodules.partdisks",
      "linstaller.core.libmodules.unsquash",
      "linstaller.modules",
      
      "linstaller.modules.bootloader",
      "linstaller.modules.bootloader.front",
      "linstaller.modules.bootloader.inst",
      
      "linstaller.modules.debian",
      "linstaller.modules.debian.inst",
      
      "linstaller.modules.mirrorselect",
      "linstaller.modules.mirrorselect.front",
      "linstaller.modules.mirrorselect.inst",
      
      "linstaller.modules.clean",
      "linstaller.modules.clean.inst",
      
      "linstaller.modules.end",
      "linstaller.modules.end.front",
      
      "linstaller.modules.fstab",
      "linstaller.modules.fstab.inst",
      
      "linstaller.modules.language",
      "linstaller.modules.language.front",
      "linstaller.modules.language.inst",
      
      "linstaller.modules.network",
      "linstaller.modules.network.inst",
      
      "linstaller.modules.partdisks",
      "linstaller.modules.partdisks.front",
      "linstaller.modules.partdisks.inst",
      
      "linstaller.modules.semplice",
#      "linstaller.modules.semplice.inst",

      "linstaller.modules.ubuntu",
      "linstaller.modules.ubuntu.inst",
      
      "linstaller.modules.summary",
      "linstaller.modules.summary.front",
      
      "linstaller.modules.timezone",
      "linstaller.modules.timezone.front",
      "linstaller.modules.timezone.inst",
      
      "linstaller.modules.unsquash",
      "linstaller.modules.unsquash.inst",
      
      "linstaller.modules.update",
      "linstaller.modules.update.front",
      
      "linstaller.modules.userhost",
      "linstaller.modules.userhost.inst",
      "linstaller.modules.userhost.front",
      
      "linstaller.modules.welcome",
      "linstaller.modules.welcome.front",
      ],
      data_files=[("/usr/bin", ["linstaller_wrapper.sh", "mount_nolive.sh"]),
      ("/etc/linstaller", ["config/semplice", "config/semplice-base", "config/semplice-nolive", "config/ubuntu", "config/ubuntu-nolive"]),
      ("/usr/share/alan/alan/ext", ["alan/linstaller_alan.py"]),
      ],
      requires=['apt.cache', 'ConfigParser', 'commands', 'copy', 'getpass', 'os', 'progressbar', 'subprocess', 'threading', 'traceback', 'debconf', 'exceptions', 'liblaiv_setup', 'operator', 'parted', 'sys', 't9n.library', 'time'],
     )
