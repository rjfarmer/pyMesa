import pyMesaUtils as pym
import sys

utils_lib, utils_def = pym.loadMod("utils")

utils_lib.utils_omp_get_max_threads()
utils_lib.utils_omp_get_thread_num()


import pymesa.pyMesaUtils as pym


class utils(object):
	def __init__(self):
		self.const_lib, self.const_def = pym.loadMod("const")
		
		self.crlibm_lib, _ = pym.loadMod("math")
		self.crlibm_lib.math_init()
		
		self.utils_lib, self.utils_def = pym.loadMod("utils")
