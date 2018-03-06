import pyMesaUtils as pym

crlibm_lib, _ = pym.loadMod("crlibm")

crlibm_lib.crlibm_init()

crlibm_lib.ln10
crlibm_lib.exp_cr(100.0)
