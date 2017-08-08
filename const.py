import gfort2py as gf
import numpy as np
import os

MESA_DIR = os.environ.get('MESA_DIR')

LIB_DIR = os.path.join(MESA_DIR,'lib')
INCLUDE_DIR = os.path.join(MESA_DIR,'include')

FOLDER = "const"

SHARED_LIB = os.path.join(LIB_DIR,"lib"+FOLDER+".so")
MODULE = os.path.join(INCLUDE_DIR,FOLDER+"_lib.mod")  

x=gf.fFort(SHARED_LIB,MODULE,rerun=True)

# Must be a variable even though it wont change, the intent out variables are returned
# in a dict from subroutine calls
ierr=0
res=x.const_init(MESA_DIR,ierr)


print(x.a2rad)
print(x.thermohaline_mixing)
print(x.mev_to_ergs)
