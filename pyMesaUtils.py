import gfort2py as gf
import numpy as np
import os

MESA_DIR = os.environ.get('MESA_DIR')

def loadMod(module):
    LIB_DIR = os.path.join(MESA_DIR,'lib')
    INCLUDE_DIR = os.path.join(MESA_DIR,'include')

    SHARED_LIB = os.path.join(LIB_DIR,"lib"+module+".so")
    MODULE_LIB = os.path.join(INCLUDE_DIR,module+"_lib.mod")  
    MODULE_DEF = os.path.join(INCLUDE_DIR,module+"_def.mod")  
    
    return gf.fFort(SHARED_LIB,MODULE_LIB,rerun=True),gf.fFort(SHARED_LIB,MODULE_DEF,rerun=True)

