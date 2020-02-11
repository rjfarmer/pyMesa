import pymesa.pyMesaUtils as pym


class chem(object):
	def __init__(self):
		self.const_lib, self.const_def = pym.loadMod("const")
		self.crlibm_lib, _ = pym.loadMod("math")
		self.crlibm_lib.math_init()
		self.const_lib.const_init(pym.MESA_DIR,0)
		self.chem_lib,self.chem_def = pym.loadMod("chem")
		self.chem_lib.chem_init('isotopes.data',0)

