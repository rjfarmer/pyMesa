#!/bin/bash

# Tool to build mesa with python support
# Licensed under GPLv2+
# Author Robert Farmer
# rjfarmer@asu.edu
# 17/09/2017


if [ -z "$MESA_DIR" ];then
    echo "MESA_DIR is unset"
    exit 1
fi


if [[ ! "$PATH" == *"$MESASDK_ROOT"* ]];then
    echo "MESASDK has not been initlized"
    exit 1
fi

MESA_VERSION=$(<"$MESA_DIR/data/version_number")


if [[ "$MESA_VERSION" == 9793 ]];then
    rm -rf "$MESA_DIR"/patches
    mkdir -p "$MESA_DIR"/patches
    for i in 0001-Build-shared-libraries.patch  0002-bug-fixes.patch  0003-crlibm-shared-library.patch;do
        cp patches/$i "$MESA_DIR"/patches/.
    done    
else
    echo "MESA version $MESA_VERSION not supported"
    echo "Open issue on github to request your mesa version"
    exit 1
fi


cd "$MESA_DIR"
echo "Clean MESA"
./clean
echo "Patching mesa"
for i in patches/*;do
    patch -p1 < $i
done
echo "Building mesa"
export LD_LIBRARY_PATH=../make:$MESA_DIR/lib:$LD_LIBRARY_PATH
./mk
echo "****************************************************************"
echo "MESA is now ready for python"
echo "Each time you wish to use this you must set the LD_LIBRARAY_PATH"
echo "After the sdk has been initilized:"
echo 'export LD_LIBRARY_PATH=$MESA_DIR/lib:$LD_LIBRARY_PATH'
echo "You do not need to run this script again unless you ran ./clean"
echo "inside your MESA_DIR"
echo "****************************************************************"
echo
echo
echo
