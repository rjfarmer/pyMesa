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

class TestMath(unittest.TestCase):
	def test_math_basic(self):
		math = pym.math.math(p.defaults)
		m1 = math.exp10_(5.2348).result
		m2 = math.math_lib.exp10_(5.2348).result
		self.assertEqual(m1,m2)
