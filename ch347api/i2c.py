#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: i2cy(i2cy@outlook.com)
# Project: CH347-HIDAPI
# Filename: i2c
# Created on: 2024/1/6


from .__device import CH347HIDDev
from .__i2c import convert_int_to_bytes
from typing import Tuple, Any


class I2CDevice:

    def __init__(self, addr: int, clock_freq_level: int = 1, ch347_device: CH347HIDDev = None):
        """
        Encapsulated class of I2C device
        :param addr: I2C device address
        :type addr: int
        :param clock_freq_level: Clock frequency, 0-20KHz, 1-100KHz, 2-400KHz, 3-750KHz
        :type clock_freq_level: int, optional
        :param ch347_device: CH347HIDDev (defaults to None), will create a new CH347HIDDev if unset
        :type ch347_device: CH347HIDDev, optional
        """
        if ch347_device is None:
            # create new CH347 HID device port if unset
            ch347_device = CH347HIDDev()

        self.dev = ch347_device
        self.addr = addr

        if not self.dev.i2c_initiated:
            # initialize i2c device if doesn't
            self.dev.init_I2C(clock_freq_level=clock_freq_level)

    def write(self, reg: (int, bytes) = None, data: (int, bytes) = None) -> bool:
        """
        Write data to the device through I2C bus
        :param reg: address of the register, or None for direct transmission
        :type reg: :obj:`int`, :obj:`bytes`
        :param data: data to send, or None for write probing
        :type data: :obj:`int`, :obj:`bytes`
        :return: operation status
        """
        payload = b""
        if reg is not None:
            payload += convert_int_to_bytes(reg)

        if data is not None:
            payload += convert_int_to_bytes(data)

        return self.dev.i2c_write(self.addr, data=payload)

    def read(self, reg: (int, bytes) = None, length: int = 0):
        """
        Read data from the device through I2C bus
        :param reg: address of the register, or None for direct transmission
        :type reg: :obj:`int`, :obj:`bytes`
        :param length: number of bytes to read, default is 0 for read probing
        :type length: int
        :return: return bytes when length is greater than 0, or bool status if length is 0
        :rtype: :obj:`bytes`, :obj:`bool`
        """
        status, feedback = self.dev.i2c_read(addr=self.addr, read_length=length, register_addr=reg)

        if length:
            return feedback
        else:
            return status
