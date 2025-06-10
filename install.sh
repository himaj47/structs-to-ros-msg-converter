#!/bin/bash

# Shell script to rebuild and reinstall a Python package locally

echo "Uninstalling existing stm_converter..."
pip uninstall -y stm_converter

echo "Building wheel and source distribution..."
python3 setup.py bdist_wheel sdist

echo "Reinstalling stm_converter from local source..."
pip install .
