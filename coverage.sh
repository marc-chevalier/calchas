#!/bin/bash
python3-coverage run --source=calchas_datamodel,calchas_transformations,calchas_polyprinter,calchas_polyparser,calchas_sympy run_tests.py
python3-coverage html
xdg-open htmlcov/index.html
