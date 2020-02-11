

# This is broken with the changes to math_lib in ~12608
# For now all you can and should do is call the init function

import pymesa.pyMesaUtils as pym


class crlibm(object):
	def __init__(self):
		self.crlibm_lib, _ = pym.loadMod("math")
		crlibm_lib.math_init()
