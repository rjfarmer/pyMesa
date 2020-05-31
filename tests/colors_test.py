# SPDX-License-Identifier: GPL-2.0+

import os, sys

os.environ["_GFORT2PY_TEST_FLAG"] = "1"

import numpy as np
import gfort2py as gf

import unittest as unittest
    
import subprocess
import numpy.testing as np_test

from contextlib import contextmanager
from io import StringIO
from io import BytesIO

#Decreases recursion depth to make debugging easier
# sys.setrecursionlimit(10)


import pymesa as pym
p=pym.mesa()
defaults = p.defaults

colors=pym.colors.colors(defaults)

class TestColors(unittest.TestCase):
	def test_basic(self):
		x=colors.get_bc('V',4.0,4.0,0.0)
		y=colors.get_bc('V',4.5,4.0,0.0)
		self.assertFalse(x==y)
		y2=colors.get_bc('B',4.5,4.0,0.0)
		self.assertFalse(y2==y)

		colors.get_abs_mag('V',4.5,4.0,0.0,1.0) 
		colors.get_lum('V',4.5,4.0,0.0,1.0)
		colors.available_names()
		colors.get_abs_bolo_mag(1.0) 
		#colors.mdivh({'h1':0.25,'he4':0.25,'c12':0.25,'o16':0.25})
