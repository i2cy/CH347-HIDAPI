<!-- markdownlint-disable MD033 MD036 MD041 -->

<div align="center">

# CH347-HIDAPI Python Library

_? [CH347-HIDAPI Github Page](https://github.com/i2cy/ch347-hidapi) ?_

</div>

<p align="center">
  <a href="https://github.com/i2cy/ch347-hidapi/master/LICENSE">
    <img src="https://img.shields.io/github/license/i2cy/ch347-hidapi.svg" alt="license">
  </a>
  <a href="https://pypi.python.org/pypi/ch347api">
    <img src="https://img.shields.io/pypi/v/ch347api.svg" alt="pypi">
  </a>
  <img src="https://img.shields.io/badge/python-3.7+-blue.svg" alt="python">
</p>

## Abstract
This project is the API library of CH347 USB-SPI bridge chip based on Python.
Standard USB-HID mode setting of CH347 chip supported only.

This library provides full access of SPI settings and communication with CH347 USB-SPI 
bridge chip in Python language.

[CH347-Chip Official Site](https://www.wch.cn/products/CH347.html)

## Installation
`pip install ch347api`

## Requirements
`Python >= 3.7`
`hidapi`

## CAUTION
The communication protocol with CH347 through USB-HID I wrote in this project based on the official
demonstration APP. In other words that it was inferred from captured HID package when APP communicates.

THUS, THIS API MAY NOT FULLY CAPABLE OF EVERY FUNCTION IN OFFICIAL API FROM CH347DLL.DLL.

And I2C API is not ready. I2C bus example from demo app is frustrating and I need time to figure it out.