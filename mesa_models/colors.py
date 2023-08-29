import pyMesa as pym
import os
import numpy as np

const_lib, const_def = pym.loadMod("const")
math_lib, _ = pym.loadMod("math")
math_lib.math_init()
ierr=0
const_lib.const_init(pym.MESA_DIR,ierr)

col_lib,col_def = pym.loadMod("colors")


ierr = 0

fnames = np.array([os.path.join(pym.DATA_DIR,'colors','lcb98cor.dat')],dtype='S')

# Currently broken in gfort2py
col_lib.colors_init(len(fnames),fnames,11,ierr)



print(col_lib.get_bc_by_name(
    'V',np.log10(5777.0), 4.5, 0.0, ierr
    ).result
)


col_lib.colors_shutdown()