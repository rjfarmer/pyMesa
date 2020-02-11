import pymesa.pyMesaUtils as pym


class atm(object):
	def __init__(self):
		self.const_lib, self.const_def = pym.loadMod("const")
		self.crlibm_lib, _ = pym.loadMod("math")
		self.crlibm_lib.math_init()
		self.const_lib.const_init(pym.MESA_DIR,0)
		self.atm_lib,self.atm_def = pym.loadMod("atm")
