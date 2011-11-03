#!/usr/bin/env python
# pylaivng setup (using distutils)
# Copyright (C) 2011 Eugenio "g7" Paolantonio. All rights reserved.
# Work released under the GNU GPL license, version 3.

from distutils.core import setup

setup(name='linstaller',
      version='1.51.0',
      description='Modular, preseedable, GNU/Linux distribution installer',
      author='Eugenio Paolantonio and the Semplice Team',
      author_email='me@medesimo.eu',
      url='http://launchpad.net/linstaller',
      scripts=['linstaller.py'],
      packages=["linstaller", "linstaller.core", "linstaller.core.libmodules",
      "linstaller.core.libmodules.chroot",
      "linstaller.core.libmodules.partdisks",
      "linstaller.core.libmodules.unsquash",
      "linstaller.modules",
      "linstaller.modules.bootloader",
      "linstaller.modules.debian",
      "linstaller.modules.end",
      "linstaller.modules.fstab",
      "linstaller.modules.language",
      "linstaller.modules.network",
      "linstaller.modules.partdisks",
      "linstaller.modules.semplice",
      "linstaller.modules.summary",
      "linstaller.modules.timezone",
      "linstaller.modules.unsquash",
      "linstaller.modules.update",
      "linstaller.modules.userhost",
      "linstaller.modules.welcome",
      ],
      data_files=[("/usr/bin", ["linstaller_wrapper.sh"]),
      ("/etc/linstaller", ["config/semplice", "config/semplice-base", "config/semplice-nolive"]),
      ("/usr/share/alan/alan/ext", ["alan/linstaller_alan.py"]),
      ],
      requires=['apt.cache', 'ConfigParser', 'commands', 'copy', 'getpass', 'os', 'progressbar', 'subprocess', 'threading', 'traceback', 'debconf', 'exceptions', 'liblaiv_setup', 'operator', 'parted', 'sys', 't9n.library', 'time'],
     )
