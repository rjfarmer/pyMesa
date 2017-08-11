# pyMesa
Allows python to interface with MESA

## Requirements:
[gfort2py](https://github.com/rjfarmer/gfort2py)

numpy

## MESA patching
Currently version 9898 plus patch (note with the patch enabled we dont use clibm, we use mesa's lapack and blas, we dont run the tests (as crlibm doesnt work) 
and anything past (and including) gyre doesnt build as gyre need functions from lapack that are not in the MESA_SRCS version of lapack, but the sdk
only ships static .a libraries when we need .so)

````bash
cd $MESA_DIR
export LD_LIBRARY_PATH=../make:$MESA_DIR/lib:$LD_LIBRARY_PATH
patch -p1 < 0001-Build-shared-libs.patch
/usr/bin/touch skip_test
./mk
cd $MESA_DIR/lib
for i in *.so;do chrpath -r $i;done

#Debug only
cd $MESA_DIR/include
for i in *.mod;do j=${i%.*};cp $i $j.gz;gunzip $j.gz;echo $i;done

````

## Running
````bash
export LD_LIBRARY_PATH=$MESA_DIR/lib:$LD_LIBRARY_PATH
python3
````

## Modules that work (somewhat)

- [x] atm.py
- [x] chem.py
- [ ] colors.py
- [x] const.py
- [x] crlibm.py (Note this is the crlibm stub)
- [x] eos.py
- [x] ion.py
- [x] kap.py
- [x] net.py
- [x] neu.py
- [x] rates.py
- [ ] utils.py





