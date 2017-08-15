![pyMesa logo](images/logo.png?raw=true "pyMesa Logo")

# pyMesa
Allows python to interface with MESA

## Requirements:
[gfort2py](https://github.com/rjfarmer/gfort2py)

numpy

## MESA patching

Find the patch for the mesa version you wishe to use in the patch folder and copy it to $MESA_DIR. Other
mesa versions can be supported on request.

Currently with this patch applied we dont use crlibm, we use mesa's lapack and blas and we dont run the test suite
(as crlibm does not work). Gyre can not currently be built for this due to dependecny issues with mesa's lapack.

````bash
cd $MESA_DIR
export LD_LIBRARY_PATH=../make:$MESA_DIR/lib:$LD_LIBRARY_PATH
patch -p1 < mesa-rXXX.patch # Replace XXXX with the patch file you copied over here
./clean
./mk
````

To reverse the changes made to the MESA folder
````bash
cd $MESA_DIR
patch -R -p1 < mesa-rXXX.patch # -R reverse the changes
./clean
./mk
````



## Running
````bash
# Set MESA_DIR and initilize the sdk

export LD_LIBRARY_PATH=$MESA_DIR/lib:$LD_LIBRARY_PATH
python3
````

Note i've found you need to redo the LD_LIBRARY_EXPORT after initilizing the sdk

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
- [x] crlibm.py (Note this is the crlibm stub so not bit for bit)
- [x] eos.py
- [x] ion.py
- [x] kap.py
- [x] net.py
- [x] neu.py
- [x] rates.py
- [ ] utils.py
- [ ] star.py




