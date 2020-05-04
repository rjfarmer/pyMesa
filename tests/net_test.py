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

class TestNet(unittest.TestCase):
	@unittest.skip("Skipping as we seg fault")	
	def test_net_basic(self):
		net=pym.net.net(defaults)
		net.net_setup('mesa_45.net')
		g = net.get_net_general_info()
		g.in_use
		try:
			g.weaklib_ids
		except pym.gf.errors.AllocationError:
			pass
			
		net.net_get({'h1':0.25,'he4':0.25,'c12':0.25,'o16':0.25},10**9,10**5)
