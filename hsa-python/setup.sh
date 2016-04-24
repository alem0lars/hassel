#!/bin/bash
echo "Add $a to PYTHONPATH."
export PYTHONPATH="$PYTHONPATH:$(pwd 2>&1)"
cd c-bytearray
python setup.py build
cp build/lib.*/c_wildcard*.so ../utils/.
rm -rf build
cd ..

