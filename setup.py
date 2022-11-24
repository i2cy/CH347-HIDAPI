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
    name="ch347api",
    version="0.0.2",
    author="I2cy Cloud",
    author_email="i2cy@outlook.com",
    description="A Python Library provides full access of SPI settings and communication"
                " with CH347 USB-SPI bridge chip in Python language.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/i2cy/ch347-hidapi",
    project_urls={
        "Bug Tracker": "https://github.com/i2cy/ch347-hidapi/issues",
        "Source Code": "https://github.com/i2cy/ch347-hidapi",
        "Documentation": "https://github.com/i2cy/CH347-HIDAPI/blob/master/README.md"
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'hidapi'
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.7",
    entry_points={'console_scripts':
                      []
                  }
)
