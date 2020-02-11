#!/usr/bin/env python

import os
from setuptools import setup, find_packages
import os
import sysconfig
		


def get_version():
	with open("pymesa/version.py") as f:
		l=f.readlines()
	return l[0].split("=")[-1].strip().replace("'","")


setup(name='pyMesa',
      version=get_version(),
      description='Python interface to the MESA stellar evolution code',
      license="GPLv2+",
      author='Robert Farmer',
      author_email='r.j.farmer@uva.nl',
      url='https://github.com/rjfarmer/pyMesa',
      keywords='MESA',
      packages=find_packages(),
      classifiers=[
			"Development Status :: 3 - Alpha",
			"License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
		    
      ]
     )
