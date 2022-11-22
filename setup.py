#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: i2cy(i2cy@outlook.com)
# Project: CH347PythonLib
# Filename: setup
# Created on: 2022/11/22

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="i2cylib",
    version="1.12.3",
    author="I2cy Cloud",
    author_email="i2cy@outlook.com",
    description="A Python library contains a lot of useful functions and tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/i2cy/i2cylib",
    project_urls={
        "Bug Tracker": "https://github.com/i2cy/i2cylib/issues",
        "Source Code": "https://github.com/i2cy/i2cylib",
        "Documentation": "https://github.com/i2cy/I2cylib/wiki/API-Document"
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'numpy',
        'tqdm',
        'rsa',
        'pyserial',
        'matplotlib'
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    entry_points={'console_scripts':
        [
            "i2cydbserver = i2cylib.database.I2DB.i2cydbserver:main",
            "i2en = i2cylib.crypto.I2En.icen:main",
            "i2scan = i2cylib.network.I2Scan.i2scan:main"
        ]
    }
)
