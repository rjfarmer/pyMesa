#!/usr/bin/env bash

cd tests

export PYTHONFAULTHANDLER=1
python3 -m unittest discover .  "*_test.py"

