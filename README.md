# pyMesa
Allows python to interface with MESA

## Requirements:
gfort2py 
numpy

## MESA
Currently version 9898 plus patch (note with the patch enabled we dont use clibm, we use mesa's lapack and blas, we dont run the tests (as crlibm doesnt work) and anything past gyre doesnt build)

````bash
cd $MESA_DIR
0001-Build-shared-libs.patch
````
