# Tool to build mesa with python support

# Copyright (C) 2023  Robert Farmer <robert.j.farmer37@gmail.com>

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

    MODULE_LIB = os.path.join(INCLUDE_DIR,f"{module}_lib.mod")
    MODULE_DEF = os.path.join(INCLUDE_DIR,f"{module}_def.mod")

    if module =='run_star_support':
         SHARED_LIB = os.path.join(LIB_DIR,f"librun_star_support.{LIB_EXT}")
         MODULE_LIB = os.path.join(INCLUDE_DIR,"run_star_support.mod")
    elif module =='run_star_extras':
         SHARED_LIB = os.path.join(LIB_DIR,f"librun_star_extras.{LIB_EXT}")
         MODULE_LIB = os.path.join(INCLUDE_DIR,"run_star_extras.mod")
    else:
        SHARED_LIB = os.path.join(LIB_DIR,f"lib{module}.{LIB_EXT}")

    x = None
    y = None

    try:
        x = gf.fFort(SHARED_LIB,MODULE_LIB)
    except FileNotFoundError:
        pass

    try:
        y = gf.fFort(SHARED_LIB,MODULE_DEF)
    except FileNotFoundError:
        pass

    return x, y


def _buildRunStarSupport():
    if os.path.exists(os.path.join(LIB_DIR,f"librun_star_support.{LIB_EXT}")):
        return

    cwd = os.getcwd()
    os.chdir(os.path.join(MESA_DIR,'star','make'))
    try:
        compile_cmd = ['gfortran -Wno-uninitialized -fno-range-check',
                      '-fPIC -shared -fprotect-parens',
                      '-fno-sign-zero -fbacktrace -ggdb',
                      '-fopenmp  -std=f2008 -Wno-error=tabs -I../public',
                      '-I../private -I../../include',
                      '-I'+os.path.join(MESASDK_ROOT,'include'),
                      '-Wunused-value -W -Wno-compare-reals',
                      '-Wno-unused-parameter -fimplicit-none  -O2',
                      '-ffree-form -x f95-cpp-input -I../defaults',
                      '-I../job -I../other ../job/run_star_support.f90',
                      '-Wl,-rpath=' + LIB_DIR,
                      '-o librun_star_support.'+LIB_EXT,
                      '-L'+LIB_DIR,
                      '-lstar -lgyre -latm -lcolors -lnet -leos',
                      '-lkap -lrates -lneu -lchem -linterp_2d -linterp_1d',
                      '-lnum -lmtx -lconst -lutils -lrun_star_extras']

        print(" ".join(compile_cmd))
        x = subprocess.call(" ".join(compile_cmd),shell=True)
        if x:
            raise ValueError("Build run_star_support failed")
        shutil.copy2(f"librun_star_support.{LIB_EXT}",os.path.join(LIB_DIR,f"librun_star_support.{LIB_EXT}"))
        shutil.copy2('run_star_support.mod',os.path.join(INCLUDE_DIR,'run_star_support.mod'))
    except:
        raise
    finally:
        os.chdir(cwd)

    os.chdir(LIB_DIR)
    _checkcrpath()
    try:
        x = subprocess.call(f"chrpath -r librun_star_support.{LIB_EXT}",shell=True)
        if x:
            raise ValueError("chrpath failed")
    except:
        raise
    finally:
        os.chdir(cwd)

    print("Built run_star_support")


def _buildRunStarExtras(rse=None):
    if os.path.exists(os.path.join(LIB_DIR,f"librun_star_extras.{LIB_EXT}")):
        return

    filename = 'run_star_extras.f'
    output = os.path.join(MESA_DIR,'star','make',filename)
    if rse is None:
        with open(output,'w') as f:
            print('module run_star_extras',file=f)
            print('use star_lib',file=f)
            print('use star_def',file=f)
            print('use const_def',file=f)
            print('implicit none',file=f)
            print('contains',file=f)
            print('include "standard_run_star_extras.inc"',file=f)
            print('end module run_star_extras',file=f)
    else:
        shutil.copy2(rse,output)

    cwd = os.getcwd()
    os.chdir(os.path.join(MESA_DIR,'star','make'))
    try:
        compile_cmd = ['gfortran -Wno-uninitialized -fno-range-check',
                      '-fPIC -shared -fprotect-parens',
                      '-fno-sign-zero -fbacktrace -ggdb',
                      '-fopenmp  -std=f2008 -Wno-error=tabs -I../public',
                      '-I../private -I../../include',
                      '-I'+os.path.join(MESASDK_ROOT,'include'),
                      '-Wunused-value -W -Wno-compare-reals',
                      '-Wno-unused-parameter -fimplicit-none  -O2',
                      '-ffree-form -x f95-cpp-input -I../defaults',
                      '-I../job -I../other',
                      filename,
                      '-Wl,-rpath=' + LIB_DIR,
                      '-o librun_star_extras.'+LIB_EXT,
                      '-L'+LIB_DIR,
                      '-lstar -lconst']

        print(" ".join(compile_cmd))
        x = subprocess.call(" ".join(compile_cmd),shell=True)
        if x:
            raise ValueError("Build run_star_extras failed")
        shutil.copy2(f"librun_star_extras.{LIB_EXT}",os.path.join(LIB_DIR,f"librun_star_extras.{LIB_EXT}"))
        shutil.copy2('run_star_extras.mod',os.path.join(INCLUDE_DIR,'run_star_extras.mod'))
    except:
        raise
    finally:
        os.chdir(cwd)

    os.chdir(LIB_DIR)
    _checkcrpath()
    try:
        x = subprocess.call(f"chrpath -r librun_star_extras.{LIB_EXT}",shell=True)
        if x:
            raise ValueError("chrpath failed")
    except:
        raise
    finally:
        os.chdir(cwd)

    print("Built run_star_extras")

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
