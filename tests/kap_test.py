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

class TestKap(unittest.TestCase):
	def test_kap_basic(self):
		kap = pym.kap.kap(p.defaults)
				
		zbar = 1.0
		X = 0.78
		Z = 0.02
		Zbase = 0.02
		XC = 0.0
		XN = 0.0
		XO = 0.0
		XNe = 0.0
		logRho = 9.0
		logT = 9.0
		lnfree_e = 0.0
		d_lnfree_e_dlnRho= 0.0
		d_lnfree_e_dlnT= 0.0
		
		kap.kap_get(zbar, X, Z, Zbase, XC, XN, XO, XNe,logRho,logT,
                lnfree_e, d_lnfree_e_dlnRho, d_lnfree_e_dlnT)
