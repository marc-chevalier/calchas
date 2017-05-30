#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name='calchas',
    version='0.2',
    description='A collection of package about computer algebra system',
    url='https://github.com/s-i-newton/calchas',
    author='Marc Chevalier',
    author_email='calchas@marc.chevalier',
    license='MIT',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Software Development :: Libraries',
    ],
    install_requires=[
        'sympy>=1.0',
        'ply>=3.10',
    ],
    packages=[
        'calchas_datamodel',
        'calchas_polyparser',
        'calchas_polyprinter',
        'calchas_sympy',
        'calchas_transformations',
    ],
)
