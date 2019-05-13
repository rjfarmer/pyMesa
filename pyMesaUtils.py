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
import subprocess


# Dependacy check
G2PY_MIN_VER='1.0.11'

class FileNotFoundError(Exception):
    pass

try:
    G2PY_VER=gf.__version__
except AttributeError:
    # Old versions didn't set __version__
    raise AttributeError("Must update gfort2py to at least version "+G2PY_MIN_VER)

def _versiontuple(v):
    return tuple(map(int, (v.split("."))))

if _versiontuple(G2PY_VER) < _versiontuple(G2PY_MIN_VER):
    raise AttributeError("Must update gfort2py to at least version "+G2PY_MIN_VER)

#MESA DIR check and path set
if "MESA_DIR" not in os.environ:
    raise ValueError("Must set MESA_DIR environment variable")
else:
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

MESASDK_ROOT=os.path.expandvars('$MESASDK_ROOT')

with open(os.path.join(DATA_DIR,'version_number'),'r') as f:
    v=f.readline().strip()
    MESA_VERSION=int(v)
    
if MESA_VERSION < 11035:
    if "LD_LIBRARY_PATH" not in os.environ:
        raise ValueError("Must set LD_LIBRARY_PATH environment variable")
    elif LIB_DIR not in os.environ['LD_LIBRARY_PATH']:
        raise ValueError("Must have $MESA_DIR/lib in LD_LIBRARY_PATH environment variable")
    
p=sys.platform.lower()

if p == "linux" or p == "linux2":
    LIB_EXT='so'
elif p == "darwin":
    LIB_EXT="dylib"
else:
    raise Exception("Platform not support "+str(p))

# The one function you actaully need
def loadMod(module):
    
    if module =='crlibm':
        SHARED_LIB = os.path.join(LIB_DIR,"libf2crlibm."+LIB_EXT)
    elif module =='run_star_support':
         SHARED_LIB = os.path.join(LIB_DIR,"librun_star_support."+LIB_EXT)
    else:
        SHARED_LIB = os.path.join(LIB_DIR,"lib"+module+"."+LIB_EXT)
        
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


def buildModule(module):
    cwd = os.getcwd()
    os.chdir(os.path.join(MESA_DIR,module))
    
    try:
        x=subprocess.call("./clean >/dev/null 2>/dev/null",shell=True)
        if x:
            raise ValueError("clean failed")
        x = subprocess.call("./build_and_test >/dev/null 2>/dev/null",shell=True)
        if x:
            raise ValueError("Build_and_test failed")
        x = subprocess.call("./export >/dev/null 2>/dev/null",shell=True)
        if x:
            raise ValueError("export failed")
    except:
        raise
    finally:
        os.chdir(cwd)
        
    if MESA_VERSION < 11035:
        os.chdir(LIB_DIR)
        try:
            x = subprocess.call("chrpath -r lib"+module+"."+LIB_EXT,shell=True)
            if x:
                raise ValueError("chrpath failed")
        except:
            raise
        finally:
            os.chdir(cwd)

    print("Built "+str(module))

def buildRunStarSupport():
    cwd = os.getcwd()
    os.chdir(os.path.join(MESA_DIR,'star','make'))
    try:
        compile_cmd = ['gfortran -Wno-uninitialized -fno-range-check',
                      '-fmax-errors=12 -fPIC -shared -fprotect-parens',
                      '-fno-sign-zero -fbacktrace -ggdb -finit-real=snan',
                      '-fopenmp  -std=f2008 -Wno-error=tabs -I../public',
                      '-I../private -I../../include',
                      '-I'+os.path.join(MESASDK_ROOT,'include'),
                      '-Wunused-value -Werror -W -Wno-compare-reals',
                      '-Wno-unused-parameter -fimplicit-none  -O2',
                      '-ffree-form -x f95-cpp-input -I../defaults',
                      '-I../job -I../other ../job/run_star_support.f90',
                      '-Wl,-rpath=' + LIB_DIR,
                      '-o librun_star_support.'+LIB_EXT]
        
        x = subprocess.call(" ".join(compile_cmd),shell=True)
        if x:
            raise ValueError("Build run_star_support failed")
    except:
        raise
    finally:
        os.chdir(cwd)
        
    os.chdir(LIB_DIR)
    try:
        x = subprocess.call("chrpath -r librun_star_support."+LIB_EXT,shell=True)
        if x:
            raise ValueError("chrpath failed")
    except:
        raise
    finally:
        os.chdir(cwd)
        
    print("Built run_star_support")
