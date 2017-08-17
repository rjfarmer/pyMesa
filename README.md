![pyMesa logo](images/logo.png?raw=true "pyMesa Logo")

# pyMesa
Allows python to interface with MESA

## Requirements:
[gfort2py](https://github.com/rjfarmer/gfort2py)

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

````python
import pyMesaUtils as pym

# Loads the const module
const_lib,const_def = pym.loadMod("const")

# Must define a variable even if its a intent out
ierr=0
# Calls a function
res = const_lib.const_init(pym.MESA_DIR,ierr)

# If the call was a subroutine then res is a dict with the intent out variables in there
# else it contains the result of the function call


# Gets a module variable
const_def.mev_to_ergs

# Define derived types as dicts when passing to a function
x = {}
# Arrays (if alloctable, intent(out), assumed etc) as empty when passing to a function
x = np.zeros(size)

````



## Modules that work (somewhat)

- [x] atm.py
- [ ] binary.py
- [x] chem.py
- [ ] colors.py
- [x] const.py
- [x] crlibm.py
- [x] eos.py
- [x] ion.py
- [x] kap.py
- [x] net.py
- [x] neu.py
- [x] rates.py
- [ ] utils.py
- [ ] star.py




