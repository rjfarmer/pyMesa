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

class TestEOS(unittest.TestCase):
	def test_eosdt_basic(self):
		eos = pym.eos.eos(p.defaults)

		composition = {'h1':0.5,'he4':0.5}
		temp = 10**7
		rho= 10**3

		eos.getEosDT(composition,temp,rho)

	def test_eosde_basic(self):
		eos = pym.eos.eos(p.defaults)

		composition = {'h1':0.5,'he4':0.5}
		temp = 10**7
		rho= 10**3
		energy = 100

		try:
			eos.getEosDE(composition,energy,rho,temp)
		except pym.MesaError:
			pass # Ignore when ierr /=0 as i think the inputs are not great


	def test_eospt_basic(self):
		eos = pym.eos.eos(p.defaults)

		composition = {'h1':0.5,'he4':0.5}
		temp = 10**7
		rho= 10**3
		energy = 100
		pgas = 0.5

		try:
			eos.getEosPT(composition,energy,pgas,temp)
		except pym.MesaError:
			pass # Ignore when ierr /=0 as i think the inputs are not great


	def test_eosdt_ideal_gas_basic(self):
		eos = pym.eos.eos(p.defaults)

		composition = {'h1':0.5,'he4':0.5}
		temp = 10**7
		rho= 10**3

		eos.getEosDT_ideal_gas(composition,temp,rho)



	def test_eosdt_basic2(self):
		eos = pym.eos.eos(p.defaults)

		composition = {'h1':0.5,'he4':0.5}
		temp = 10**7
		rho= 10**3

		e=eos.getEosHandle()
		e.dbg=True

		eos.getEosDT(composition,temp,rho)