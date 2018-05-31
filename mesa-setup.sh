#!/bin/bash

# Tool to build mesa with python support
# Copyright (C) 2017  Robert Farmer <r.j.farmer@uva.nl>

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



#See bug #1
if [ "$(uname)" -eq "Darwin" ];then
	echo "pyMesa does not currently work with Macs"
	echo "See https://github.com/rjfarmer/pyMesa/issues/1"
	exit 1
fi


if [ -z "$MESA_DIR" ];then
    echo "MESA_DIR is unset"
    exit 1
fi

if [ -z "$MESASDK_ROOT" ];then
    echo "MESASDK_ROOT is unset"
    exit 1
fi

if [[ ! "$PATH" == *"$MESASDK_ROOT"* ]];then
    echo "MESASDK has not been initlized"
    exit 1
fi

MESA_VERSION=$(<"$MESA_DIR/data/version_number")

SDK_HAS_LAPACK_SO="0"
if [[ -e "$MESASDK_ROOT"/lib/liblapack.so ]];then
    SDK_HAS_LAPACK_SO="1"
fi


rm -rf "$MESA_DIR"/patches
mkdir -p "$MESA_DIR"/patches


#Set override if enabled:
if [ ! -z "$PYMESA_OVERRIDE" ]
then
    MESA_VERSION="$PYMESA_OVERRIDE"
fi


if [[ "$MESA_VERSION" == 9793 ]]
then
    for i in 0001-Build-shared-libraries.patch  0002-bug-fixes.patch  0003-crlibm-shared-library.patch;
    do
        cp patches/$i "$MESA_DIR"/patches/.
    done 
    
    if [[ "$SDK_HAS_LAPACK_SO" == "1" ]]; then
        cp patches/0004-sdk-with-lapack.patch "$MESA_DIR"/patches/.
    fi
elif [[ "$MESA_VERSION" == 10000 ]]
then
    for i in 0001-build-shared-libs-10000.patch 0002-build-crlibm-10000.patch;
    do
        cp patches/$i "$MESA_DIR"/patches/.
    done  
    
    if [[ "$SDK_HAS_LAPACK_SO" == "1" ]]; then
        cp patches/0003-sdk-with-lapack-10000.patch "$MESA_DIR"/patches/.
    fi
elif [[ "$MESA_VERSION" == 10108 ]] || [[ "$MESA_VERSION" == 10398 ]]
then
    for i in 0001-build-shared-libs-10108.patch 0002-build-crlibm-10108.patch;
    do
        cp patches/$i "$MESA_DIR"/patches/.
    done  
    
    if [[ "$SDK_HAS_LAPACK_SO" == "1" ]]; then
        cp patches/0003-sdk-with-lapack-10000.patch "$MESA_DIR"/patches/.
    fi
        
else
    echo "MESA version $MESA_VERSION is not supported"
    echo "Open an issue on github to request your mesa version"
    exit 1
fi

if [[ "$PYMESA_PATCH_INIT" == 1 ]]
then
    exit 0
fi


cd "$MESA_DIR"
echo "Clean MESA"
./clean

#Skip Tests in star as we can't run a full model yet
/usr/bin/touch star/skip_test
/usr/bin/touch binary/skip_test

echo "Patching mesa"

mkdir -p "$MESA_DIR/crlibm/crlibm-patches"

for i in patches/*;
do
    patch -f -p1 < $i
done
echo "Building mesa"

if [[ "$PYMESA_PATCH_ONLY" == 1 ]]
then
    exit 0
fi

export LD_LIBRARY_PATH=../make:$MESA_DIR/lib:$LD_LIBRARY_PATH
./mk
if [[ $? != 0 ]] || [[ ! -f "$MESA_DIR/lib/libstar.so" ]] ;then
    echo
    echo
    echo
    echo "****************************************************************"
    echo "pyMESA building fail"
    echo "****************************************************************"
    echo
    echo
    echo
    exit 1
fi

echo "****************************************************************"
echo "pyMESA build was succesfull"
echo "Each time you wish to use this you must set the LD_LIBRARAY_PATH"
echo "After the sdk has been initilized:"
echo 'export LD_LIBRARY_PATH=$MESA_DIR/lib:$LD_LIBRARY_PATH'
echo "You do not need to run this script again unless you ran ./clean"
echo "inside your MESA_DIR"
echo "****************************************************************"
echo
echo
echo
