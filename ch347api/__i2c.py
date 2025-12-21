#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: i2cy(i2cy@outlook.com)
# Project: CH347PythonLib
# Filename: __i2c
# Created on: 2023/7/31


from typing import Any
import struct


class I2CClockFreq:
    f_20K = 0
    f_100K = 1
    f_400K = 2
    f_750K = 3


def convert_i2c_address(addr: (int, bytes), read: bool = False) -> bytes:
    """
    static method for address conversion
    :param addr: Any[int, bytes], 7-bits of device address
    :param read: bool, False -> write, True -> read
    :return: bytes
    """
    if isinstance(addr, int):
        addr = addr << 1
    else:
        addr = addr[0] << 1

    if read:
        addr += 1

    return struct.pack('B', addr)


def convert_int_to_bytes(inputs: (int, bytes)) -> bytes:
    """
    this method will automatically convert it into bytes with byte order 'big' unsigned if data type is int,
    e.g. 0x00f1f2 -> b'\xf1\xf2'
    :param inputs: Any[int, bytes]
    :return: bytes
    """
    if isinstance(inputs, int):
        b_len = 0
        data_copy = inputs
        while data_copy:
            b_len += 1
            data_copy = data_copy // 256
        if b_len == 0:
            b_len = 1 
        inputs = inputs.to_bytes(b_len, 'big', signed=False)
        

    return inputs
