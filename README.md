<!-- markdownlint-disable MD033 MD036 MD041 -->

<div align="center">

# CH347-HIDAPI Python Library

_+ [CH347-HIDAPI Github Page](https://github.com/i2cy/ch347-hidapi) +_

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
This project is the API library of CH347 USB-SPI/I2C bridge chip based on Python.

`Standard USB-HID mode setting of CH347 chip supported only`

This library provides full access of SPI/I2C settings and communication with CH347 USB-SPI 
bridge chip in Python language.

For demonstration and code reference please refer to the `demo.py` file in [source page](https://github.com/i2cy/CH347-HIDAPI/blob/master/demo.py).

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

## Update Notes

#### 2024-01-08
 1. Added independent I2C interface class objects (I2CDevice) and SPI interface class objects (SPIDevice)
 2. Added new demo file `demo.py` to demonstrate the usage of classes added above (simplified code)

#### 2023-08-06
 1. Now with fully compatible I2C support, I2C clock speed level: 0 -> 20KHz, 1 -> 100KHz, 2 -> 400KHz, 3 -> 750KHz
 2. Added test.py for demonstration
