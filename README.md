![pyMesa logo](images/logo.png)

[![DOI](https://zenodo.org/badge/98320319.svg)](https://zenodo.org/badge/latestdoi/98320319)


# pyMesa
pyMesa is a library allowing for the interface of the MESA stellar evolution tool with python.

It contains:
* Tools for downloading and install MESA and the MESASDK
* Interface to the individual MESA modules (eos, kap etc)
* Interface into mesastar, allowing for full control over the evolution of a star

Current stable version is 2.0.0


## Requirements:
Note: pyMesa currently only works on linux.

[gfort2py](https://github.com/rjfarmer/gfort2py) (Also available via pip) (needs version >= 1.1.5)

numpy

matplotlib

chrpath

MESA > 12829
 
## Building

### Installation

````
python3 setup.py install --user
````

### Basic usage

````python
import pymesa as pym

p=pym.mesa(MESA_DIR,MESASDK_ROOT)

````

Where MESA_DIR and MESASDK_ROOT are strings containing the path to where MESA_DIR and MESASDK_ROOT
are installed, or where you want them installed.


## Installing MESA

````python
import pymesa as pym

p=pym.mesa(MESA_DIR,MESASDK_ROOT) 
# MESA_DIR and MESASDK_ROOT do not need to exist yet but their parent folder should

# Lists available MESA or MESASDK versions
p.listMesaVersions()
p.listSDKVersions()


# Both preinstall functions take a version argument, leave empty to get the newest version

p.preinstallSDK() # Download latest SDK
p.installSDK() # Install SDK

# Downloads MESA, pass zip_src=True to get ZIP folder (release versions of mesa)
# or zip_src=False to download from SVN. Defaults to True

p.preinstallMesa() # Download MESA
p.installMesa() # Installs MESA

````


## MESA Modules

This is for interfacing with modules like eos, kap, rates etc. The star and binary
modules are interfaced in a different way.

A number of modules have wrappers around the MESA functions

````python
import pymesa as pym

p=pym.mesa(MESA_DIR,MESASDK_ROOT)

# This is a dict containing a number of default options for all the modules
defaults = p.defaults

eos = pym.eos.eos(p.defaults)

composition = {'h1':0.5,'he4':0.5}
temp = 10**7
rho= 10**3

eos.getEosDT(composition,temp,rho)
````

This then returns a dict containing the results of eosDT_get().


If the function does not have a wrapper, then the functions and 
parameters are exposed via module.module_lib and module.module_def objects:

````python
import pymesa as pym

p=pym.mesa(MESA_DIR,MESASDK_ROOT)

defaults = p.defaults

# Initialize a module
const = pym.const.const(p.defaults) 

# Access a variable inside the modules _def.f90 file
print(const.const_def.amu) 

# Access a function/subroutine inside a _lib.f90 file
chem = pym.chem.chem(p.defaults) 
chem.chem_lib.chem_get_element_id('h1')
````


### Accessing low level functions

When calling a function from a lib.f90, you must provide a variable for
all arguments the function takes, even if the argument is intent inout or out,
in which case they can be a null variable (0,'',np.zeros(1)). Otherwise
the variable you pass should be of the same type as what fortran expects:

| Fortran | Python |
|---------|--------|
| integer | int    |
| real    | float  |
| real(dp)| float  |
| logical | boolean|
| character| str    |
| dimension(n) | np.array(n) where you know how big n is already | 
dimension(5) | np.array(5)  |

Derived types should pass a dict 

Arrays with dimension(:) should pass an array of the same shape as what fortran expects

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


### Running a full star

Star is special as star_lib and star_def are not that useful on there own, instead there is a wrapper to evolve a star:


````python
import pymesa as pym

p=pym.mesa(MESA_DIR,MESASDK_ROOT)

defaults = p.defaults

# Initialize a module
s = pym.star.star(defaults) 
# star can also accept a path to a run_star_extras.f90 to use, use rse=path


pym.make_basic_inlist() # Or have a file in the current directory called 'inlist'


# Init new star
s.new_star()
s.evolve() # Run till end or hit ctrl+c

# Get output
s.get_hist('star_age')
s.get_prof('dm',1)


mass=s.get_prof_nz('mass')
temp=s.get_prof_nz('logT')    

# Plot output
import matplotlib.pyplot as plt
plt.plot(mass,temp)
plt.show()
````

Or if you want to run step by step

````python
import pymesa as pym

p=pym.mesa(MESA_DIR,MESASDK_ROOT)

defaults = p.defaults

# Initialize a module
s = pym.star.star(p.defaults) 

pym.make_basic_inlist() # Or have a file in the current directory called 'inlist'

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

res = s.star_lib.star_set_v_flag(s.star_id, True, 0) # Can call any star_lib function that takes id instead of s
pym.error_check(res) # Things that have ierr should be checked with error_check

s.single_evolve() # One step

s.after_evolve_loop() # End evolution

````

There is limited support for changing options, the best bet is to put it in a inlist and don't call make_basic_inlist().


You can only access history or profile data for output, there is no generic access to the star_type derived type.

## Bug reports:

Bug reports should go to the issue tracker on github. Please include mesa version, gfortran version, gfort2py version and pyMesa version 

## Contributing

Bug reports, if mesa versions don't work, or new examples are welcome as either pull requests
or issues on the github tracker. Wrappers around commonly used MESA functions are also welcome,
see the eos.py or neu.py for examples.

## Citating

People who use pyMESA in papers should cite this using the zenodo link for the version they used. If you use pyMesa in a project (research or teaching), let me know and i can help advertise here (also useful for me to help
with funding requests). Current versions citation is in the CITATION file.

## Known Projects using pyMesa

[Poelarends et al 2017](https://ui.adsabs.harvard.edu/#abs/2017ApJ...850..197P/abstract)


