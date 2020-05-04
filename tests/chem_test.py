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

class TestChem(unittest.TestCase):
	def test_chem_basic(self):
		chem = pym.chem.chem(p.defaults)
		chem.chem_lib.chem_get_element_id('h1')
		
		chem.chem_lib.chem_get_iso_id('he4')
	
	def test_chem_basic_composition_info(self):
		chem = pym.chem.chem(p.defaults)
		chem.basic_composition_info({'h1':0.25,'he4':0.25,'c12':0.25,'o16':0.25})
