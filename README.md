![pyMesa logo](images/logo.png)

[![DOI](https://zenodo.org/badge/98320319.svg)](https://zenodo.org/badge/latestdoi/98320319)


# pyMesa
Allows python to interface with MESA.



## Requirements:
[gfort2py](https://github.com/rjfarmer/gfort2py) (Available via pip)

numpy

libtool

## MESA patching

Run the mesa-setup.sh script from this folder, after setting MESA_DIR and initilizing the SDK.

````bash
chmod u+x mesa-setup.sh
./mesa-setup.sh
````

This script should only be run once to setup up mesa. It can be ran again if you do a ./clean inside the MESA_DIR.

We use mesa's lapack and blas and we dont run the test suite
(as mesa's bundled lapack/blas are not bit-for-bit with the sdk's). 
Gyre can not currently be built for this due to dependency issues with mesa's lapack.
Who knows about adipls i didnt even try.

Thus currently accessing things vi the python interface is not guarenteed to be bit-for-bit with MESA via fortran.

## Supported MESA versions
- 9793

Other versions can be supported upon request.


## Running
````bash
# Set MESA_DIR and initilize the sdk

export LD_LIBRARY_PATH=$MESA_DIR/lib:$LD_LIBRARY_PATH
python3
````

## Usage

Here is a basic example of talking to the const/ module, more advanced versions can be seen in the different .py files shipped.

````python
import pyMesaUtils as pym

# Loads the const module
const_lib,const_def = pym.loadMod("const")

# When calling a function we must either the value we want (for intent in variables) or an empty variable for intent outs.
ierr=0
# Calls a function
res = const_lib.const_init(pym.MESA_DIR,ierr)

# pyMesa module defines a number of useful MESA paths as pym.SOMETHING

# If the call was a subroutine then res is a dict with the intent out variables in there
# else it contains the result of the function call


# Accessing a varaiable defined in a module is simply:
const_def.mev_to_ergs

# IF the varaiable is not a parameter then you can change it with:
const_def.standard_cgrav = 5.0

# When passing a derived type, you should pass a dict to the function (filled with anything you want set)
x = {}

# Functions accepting arrays should pass a numpy array the size it expects (it the function allocates the array, then just pass a array of size 1)
x = np.zeros(size)

# Arrays inside derived types are unstable at the moment and don't completely work.

````

Function names and module variabales are all tab complteable.


## Modules that work

- [x] atm.py
- [ ] binary.py
- [x] chem.py
- [ ] colors.py
- [x] const.py
- [x] crlibm.py
- [x] eos.py
- [x] ion.py
- [x] kap.py
- [ ] net.py
- [x] neu.py
- [x] rates.py
- [ ] utils.py
- [ ] star.py

## Unistalling

The best bet is just to redownload mesa, during the setup phase we alter alot of files

## Bug reports:

Bug reports should go to the issue tracker on github. Please include mesa version and gfortran version


