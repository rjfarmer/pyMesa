![pyMesa logo](images/logo.png)

[![DOI](https://zenodo.org/badge/98320319.svg)](https://zenodo.org/badge/latestdoi/98320319)


# pyMesa
Allows python to interface with MESA. Current stable version is 1.0.2



## Requirements:
[gfort2py](https://github.com/rjfarmer/gfort2py) (Available via pip)

numpy

libtool

automake

chrpath

patch 

## Building

### SDK's

Grab a recent (atleast the september 2017 version) sdk from:

[mesasdk](http://www.astro.wisc.edu/~townsend/static.php?ref=mesasdk)

### MESA patching

Run the mesa-setup.sh script from this folder, after setting MESA_DIR and initializing the SDK.

````bash
chmod u+x mesa-setup.sh
./mesa-setup.sh
````

This script should only be run once to setup up mesa. It can be ran again if you do a ./clean inside the MESA_DIR.

Adipls, gyre and stella are not currently built as part of this.

While we can use the individual MESA modules we can not currently run a full star (or binary) model, in either python or fortran.

## Supported MESA versions
- 9793
- 10000
- 10108

Other versions can be supported upon request.

If you want to play with fire and try with another version, then set the environment variable:

````bash
export PYMESA_OVERRIDE=A_MESA_VERSION
````

Will override the version check and attempt to build MESA using the patches for the version specified. things may not work between versions if MESA's build system changes.

## Running
````bash
# Set MESA_DIR and initialize the sdk

export LD_LIBRARY_PATH=$MESA_DIR/lib:$LD_LIBRARY_PATH
python3
````

## Usage

Here is a basic example of talking to the const/ module, more advanced versions can be seen in the different .py files shipped.
Note the only python file that actualy matters is the pyMesaUtils.py file, the other python files (eos, rates etc) are mearly examples of using pyMESA for that module from MESA.

````python
# JUst need to make sure the pyMesaUtils.py file is visible either in the local directory or in PYHTHONPATH
# It does not need to be in the MESA folder.
import pyMesaUtils as pym

# Loads the const module
const_lib,const_def = pym.loadMod("const")

# When calling a function we must either set the value we want (for intent in variables) or an empty variable for intent outs.
ierr=0
# Calls a function
res = const_lib.const_init(pym.MESA_DIR,ierr)

# pyMesa module defines a number of useful MESA paths as pym.SOMETHING

# If the call was a subroutine then res is a dict with the intent out variables in there
# else it contains the result of the function call


# Accessing a variable defined in a module is simply:
const_def.mev_to_ergs

# If the variable is not a parameter then you can change it with:
const_def.standard_cgrav = 5.0

# When passing a derived type, you should pass a dict to the function (filled with anything you want set)
x = {}

# Functions accepting arrays should pass a numpy array the size it expects (if the function allocates the array, then just pass an array of size 1)
x = np.zeros(size)

# Arrays inside derived types are unstable at the moment and don't completely work.

````

Function names and module variables are all tab completable.

## Arrays

Remember that fortran has 1-based arrays while numpy uses 0-based. This comes
up if you're accessing an array via a mesa constant:

````python
mesa_array[mesa_module.i_mesa_const.get()]
````
 should instead be accessed as:
 
 ````python
mesa_array[mesa_module.i_mesa_const.get()-1]
````
An example of this can be found in eos.py.



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
- [ ] net.py (partial support)
- [x] neu.py
- [x] rates.py
- [ ] utils.py
- [ ] star.py

## Uninstalling

The best bet is just to redownload mesa, during the setup phase we alter alot of files. If you want to try to keep your MESA_DIR then something like this should work:

````bash
cd $MESA_DIR
./clean
for i in $(ls patches/* | sort -r);
do
    patch -R -p1 < $i
done

for i in $(ls crlibm/crlibm-patches/* | sort -r);
do 
    patch -R -p1 < $i
done    

rm -rf $MESA_DIR/crlibm/crlibm-patches $MESA_DIR/{star,binary}/skip_test

````


## Bug reports:

Bug reports should go to the issue tracker on github. Please include mesa version, gfortran version, gfort2py version and pyMesa version 

## Contributing

In general most of the development should go towards the gfort2py project to add new
fortran features. This repository just handles building mesa for python support. Either
bug reports, if mesa versions don't work, or new examples are welcome as either pull requests
or issues on the github tracker.

People who use pyMESA in papers should cite this useing the zenodo link for the version they used. 
