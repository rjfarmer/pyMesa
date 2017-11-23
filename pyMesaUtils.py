# Tool to build mesa with python support

# Copyright (C) 2017  Robert Farmer <r.j.farmer@uva.nl>

#This file is part of pyMesa.

#pyMesa is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 2 of the License, or
#(at your option) any later version.

#pyMesa is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with pyMesa. If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function
import gfort2py as gf
import numpy as np
import os
import sys

if "MESA_DIR" not in os.environ:
    raise ValueError("Must set MESA_DIR environment variable")

MESA_DIR = os.environ.get('MESA_DIR')



DATA_DIR = os.path.join(MESA_DIR,'data')
LIB_DIR = os.path.join(MESA_DIR,'lib')
INCLUDE_DIR = os.path.join(MESA_DIR,'include')


RATES_DATA=os.path.join(DATA_DIR,'rates_data')
EOSDT_DATA=os.path.join(DATA_DIR,'eosDT_data')
EOSPT_DATA=os.path.join(DATA_DIR,'eosPT_data')
ION_DATA=os.path.join(DATA_DIR,'ionization_data')
KAP_DATA=os.path.join(DATA_DIR,'kap_data')

NET_DATA=os.path.join(DATA_DIR,'net_data')

RATES_CACHE=os.path.join(RATES_DATA,'cache')
EOSDT_CACHE=os.path.join(EOSDT_DATA,'cache')
EOSPT_CACHE=os.path.join(EOSPT_DATA,'cache')
ION_CACHE=os.path.join(ION_DATA,'cache')
KAP_CACHE=os.path.join(KAP_DATA,'cache')
NETS=os.path.join(NET_DATA,'nets')

with open(os.path.join(DATA_DIR,'version_number'),'r') as f:
    v=f.readline().strip()
    MESA_VERSION=int(v)


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

