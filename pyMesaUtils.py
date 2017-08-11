from __future__ import print_function
import gfort2py as gf
import numpy as np
import os
import six
import sys


MESA_DIR = os.environ.get('MESA_DIR')
DATA_DIR = os.path.join(MESA_DIR,'data')
LIB_DIR = os.path.join(MESA_DIR,'lib')
INCLUDE_DIR = os.path.join(MESA_DIR,'include')

RATES_CACHE=os.path.join(DATA_DIR,'rates_data','cache')
EOSDT_CACHE=os.path.join(DATA_DIR,'eosDT_data','cache')
EOSPT_CACHE=os.path.join(DATA_DIR,'reosPT_data','cache')
ION_CACHE=os.path.join(DATA_DIR,'ionization_data','cache')
KAP_CACHE=os.path.join(DATA_DIR,'kap_data','cache')




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

