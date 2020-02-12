![pyMesa logo](images/logo.png)

[![DOI](https://zenodo.org/badge/98320319.svg)](https://zenodo.org/badge/latestdoi/98320319)


# pyMesa
Allows python to interface with MESA stellar evolution code. Current stable version is 2.0.0


## Requirements:
Note: pyMesa currently only works on linux, macs will fail to build.

[gfort2py](https://github.com/rjfarmer/gfort2py) (Also available via pip) (needs version >= 1.1.5)

numpy

matplotlib

chrpath

MESA > 12708
 
## Building

### Installation

````
python3 setup.py install --user
````


### SDK's

Grab the most recent sdk from:

[mesasdk](http://www.astro.wisc.edu/~townsend/static.php?ref=mesasdk)

### MESA patching

Edit $MESA_DIR/utils/makefile_header and set 

````
USE_SHARED = yes
````


## Usage

Each mesa module can be imported separately:

````
import pyMesa as pym
import pyMesa.const as const
````

then you can access the functions/variables as:

````
c = cosnt.const()
c.const_def.agesol
c.const_lib.const_init(pym.MESA_DIR, 0)
````

In general you don't need to run any init function yourself, that will be called when you initialize an object.


Some modules will have easier to use wrappers which are accessed at the top level of each object:

````
import pyMesa.ion as ion


ionize = ion.ion()
ionize.getIon()

````


````python
# pyMesa module defines a number of useful MESA paths as pym.SOMETHING.
print(pym.MESA_DIR) # Print MESA_DIR
print(pym.MESA_VERSION) # Print MESA version number


# When calling a function we must either set the value we want (for intent(in/inout) variables) or an empty variable for intent(out).
ierr=0
# Calls a function
res = c.const_lib.const_init(pym.MESA_DIR,ierr)


# If the call was a subroutine then res is a dict with the intent out variables in there
# else it contains the result of the function call

# Accessing a variable defined in a module is simply:
c.const_def.mev_to_ergs

# If the variable is not a parameter then you can change it with:
c.const_def.standard_cgrav = 5.0

# When passing a derived type, you should pass a dict to the function (filled with anything you want set)
x = {}
# or
x = {'a':1,'b':'abc','c':{'d':1}}

# Functions accepting arrays should pass a numpy array of the size it expects (if the function allocates the array, then just pass an array of size 1)
x = np.zeros(size)

# Arrays inside derived types are unstable at the moment and don't completely work.

````

Function names and module variables are all tab completable.

## Arrays

Remember that fortran has 1-based arrays while numpy uses 0-based. This comes
up if you're accessing an array via a mesa constant:

````python
mesa_array[mesa_module.i_mesa_const]
````
 should instead be accessed as:
 
 ````python
mesa_array[mesa_module.i_mesa_const-1]
````


### Star

Star is special as star_lib and star_def are not that useful on there own, instead there is a wrapper to evolve a star:


````python
import pyMesa as pym
import pyMesa.star as star

pym.make_basic_inlist() # Or have a file in cwd called 'inlist'
s = star.pyStar()

# Init new star
s.new_star()
s.evolve() # Run till end or hit ctrl+c

# Get output
s.get_hist('star_age')
s.get_prof('dm',1)

mass=s.get_prof_nz('mass')
temp=s.get_prof_nz('logT')    
import matplotlib.pyplot as plt
plt.plot(mass,temp)
plt.show()
````

Or if you want to run step by step

````python
import pyMesa as pym
import pyMesa.star as star

pym.make_basic_inlist() # Or have a file in cwd called 'inlist'

s = pyStar()
s.new_star()
s.before_evolve_loop()

s.single_evolve() # One step

print(s.get_hist('star_age'))
print(s.get_prof('dm',1))
print(s.get_hist('star_mass'))
print(s.controls['initial_mass'])

# Change the timestep
print(s.get_dt())
s.set_dt(s.get_dt()/2.0)
print(s.get_dt())

s.star.star_set_v_flag(s.star_id, True, 0) # Can call any star_lib function that takes id instead of s

s.single_evolve() # One step

s.after_evolve_loop() # End evolution

````

There is limited support for changing options, the best bet is to put it in a inlist and don't call make_basic_inlist().


You can only access history or profile data for output, there is no generic access to the star_type derived type.

## Bug reports:

Bug reports should go to the issue tracker on github. Please include mesa version, gfortran version, gfort2py version and pyMesa version 

## Contributing

In general most of the development should go towards the gfort2py project to add new
fortran features. This repository just handles building mesa for python support. 

Bug reports, if mesa versions don't work, or new examples are welcome as either pull requests
or issues on the github tracker.

## Citating

People who use pyMESA in papers should cite this using the zenodo link for the version they used. If you use pyMesa in a project (research or teaching), let me know and i can help advertise here (also useful for me to help
with funding requests). Current versions citation is in the CITATION file.

## Known Projects using pyMesa

[Poelarends et al 2017](https://ui.adsabs.harvard.edu/#abs/2017ApJ...850..197P/abstract)


