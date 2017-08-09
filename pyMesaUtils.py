import gfort2py as gf
import numpy as np
import os

MESA_DIR = os.environ.get('MESA_DIR')
DATA_DIR = os.path.join(MESA_DIR,'data')
LIB_DIR = os.path.join(MESA_DIR,'lib')
INCLUDE_DIR = os.path.join(MESA_DIR,'include')

def loadMod(module):
    LIB_DIR = os.path.join(MESA_DIR,'lib')
    INCLUDE_DIR = os.path.join(MESA_DIR,'include')

    if module =='crlibm':
        SHARED_LIB = os.path.join(LIB_DIR,"libf2crlibm.so")
    else:
        SHARED_LIB = os.path.join(LIB_DIR,"lib"+module+".so")
    MODULE_LIB = os.path.join(INCLUDE_DIR,module+"_lib.mod")  
    MODULE_DEF = os.path.join(INCLUDE_DIR,module+"_def.mod")  
    
    x = None
    y = None
    
    try:
        x = gf.fFort(SHARED_LIB,MODULE_LIB,rerun=True)
    except FileNotFoundError:
        pass
        
    try:
        y = gf.fFort(SHARED_LIB,MODULE_DEF,rerun=True)
    except FileNotFoundError:
        pass
    
    return x, y

