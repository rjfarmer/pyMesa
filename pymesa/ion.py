import pymesa.pyMesaUtils as pym


class ion(object):
	def __init__(self):
		self.const_lib, self.const_def = pym.loadMod("const")
		self.crlibm_lib, _ = pym.loadMod("math")
		self.crlibm_lib.math_init()
		self.const_lib.const_init(pym.MESA_DIR,0)
		self.ion_lib, self.ion_def = pym.loadMod("ionization")
		self.ion_lib.ionization_init('ion','',pym.ION_CACHE,False,0)


	def getIon(self):
		Z = 0.02
		X = 0.78
		Rho = 10**9
		log10Rho = np.log10(Rho)
		T = 10**9
		log10T = np.log10(T)
		res = np.zeros(ion_def.num_ion_vals.get())
		ierr = 0

		res = ion_lib.eval_ionization(Z, X, Rho, log10Rho, T, log10T, res, ierr)
