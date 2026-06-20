# SPDX-License-Identifier: GPL-2.0+

import gfort2py as gf
import os
import sys
import shutil
import subprocess


#MESA DIR check and path set
if "MESA_DIR" not in os.environ:
    raise ValueError("Must set MESA_DIR environment variable")
else:
    MESA_DIR = os.environ.get('MESA_DIR')

# Gfort2py version check
if not gf.__version__.startswith('3.'):
    raise ValueError(f"Unsupported gfort2py version {gf.__version__}, must be greater than 3.0.0")



DATA_DIR = os.path.join(MESA_DIR,'data')
BUILD_DIR = os.path.join(MESA_DIR,'build')
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
    if not v.startswith('r2') and len(v)<7:
        raise ValueError(f"Unsupported MESA version {v}")


p=sys.platform.lower()

if p == "linux" or p == "linux2":
    LIB_EXT='so'
elif p == "darwin":
    LIB_EXT="dylib"
else:
    raise Exception(f"Platform not support {p}")

# The one function you actually need
def loadMod(module):

    MODULE_LIB = os.path.join(BUILD_DIR,module,'include',f"{module}_lib.mod")
    MODULE_DEF = os.path.join(BUILD_DIR,module,'include',f"{module}_def.mod")

    if module =='run_star_support':
         SHARED_LIB = os.path.join(BUILD_DIR,f"librun_star_support.{LIB_EXT}")
         MODULE_LIB = os.path.join(INCLUDE_DIR,"run_star_support.mod")
    elif module =='run_star_extras':
         SHARED_LIB = os.path.join(BUILD_DIR,f"librun_star_extras.{LIB_EXT}")
         MODULE_LIB = os.path.join(INCLUDE_DIR,"run_star_extras.mod")
    else:
        SHARED_LIB = os.path.join(BUILD_DIR,module,'lib',f"lib{module}.{LIB_EXT}")

    x = None
    y = None

    try:
        x = gf.fFort(SHARED_LIB,MODULE_LIB)
    except FileNotFoundError:
        # Check if static library exists, if so warn
        if os.path.exists(os.path.join(BUILD_DIR,module,'lib',f"lib{module}.a")):
            raise MesaError(f"Shared library for {module} not found, but static library exists. Please build with shared libraries enabled.")
        pass

    try:
        y = gf.fFort(SHARED_LIB,MODULE_DEF)
    except FileNotFoundError:
        pass

    return x, y


def _buildRunStarSupport():
    raise NotImplementedError("Building run star support no longer supported")


def _buildRunStarExtras(rse=None):
    raise NotImplementedError("Building run star extras no longer supported")

class MesaError(Exception):
    pass


def _checkcrpath():
	res = subprocess.call(["command","-v","chrpath"])
	if res:
		raise ValueError("Please install chrpath")


def make_basic_inlist():
	with open('inlist','w') as f:
		print('&star_job',file=f)
		print('/',file=f)
		print('&controls',file=f)
		print('/',file=f)
		print('&pgstar',file=f)
		print('/',file=f)


def mesa_init():
    _buildRunStarExtras()
    _buildRunStarSupport()
