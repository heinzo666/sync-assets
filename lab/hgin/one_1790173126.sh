#!/bin/bash
echo ONELINE PY=$(command -v python3||echo no_py) PYV=$([ -x "$(command -v python3)" ]&&python3 -V 2>&1) ND=$(command -v node||echo no_node) PHP=$(command -v php||echo no_php) PERL=$(command -v perl||echo no_perl)
