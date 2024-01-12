#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: i2cy(i2cy@outlook.com)
# Project: CH347PythonLib
# Filename: __init__
# Created on: 2022/11/11

from .__device import CH347HIDDev, VENDOR_ID, PRODUCT_ID
from .i2c import I2CDevice
from .spi import SPIDevice
from .uart import UARTDevice
from .__spi import SPIClockFreq
from .__i2c import I2CClockFreq
