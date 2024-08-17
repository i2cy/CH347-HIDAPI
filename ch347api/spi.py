#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: i2cy(i2cy@outlook.com)
# Project: CH347-HIDAPI
# Filename: spi
# Created on: 2024/1/6


from .__device import CH347HIDDev
from .__spi import SPIClockFreq


class SPIDevice:

    def __init__(self, clock_freq_level: int = 1, is_MSB: bool = True,
                 mode: int = 0, write_read_interval: int = 0,
                 CS1_high: bool = False, CS2_high: bool = False,
                 is_16bits: bool = False,
                 ch347_device: CH347HIDDev = None):
        """
        Encapsulated class of SPI device
        :param clock_freq_level: clock freq, 0=60M, 1=30M, 2=15M, 3=7.5M, 4=3.75M, 5=1.875M, 6=937.5K，7=468.75K
        :type clock_freq_level: int
        :param is_MSB: enable MSB mode
        :type is_MSB: bool
        :param mode: set SPI mode, can only be 0, 1, 2, 3
        :type mode: int
        :param write_read_interval: set SPI write read interval value
        :type write_read_interval: int
        :param CS1_high: set SPI CS1 port polarity, True=Active-High, False=Active-Low
        :type CS1_high: bool
        :param CS2_high: set SPI CS1 port polarity, True=Active-High, False=Active-Low
        :type CS2_high: bool
        :param is_16bits: set SPI 16-bit mode
        :type is_16bits: bool
        :param ch347_device: (defaults to None), will create a new CH347HIDDev if unset
        :type ch347_device: CH347HIDDev, optional
        """
        if ch347_device is None:
            # create new CH347 HID device port if unset
            ch347_device = CH347HIDDev()

        self.dev = ch347_device
        if not self.dev.spi_initiated:
            self.dev.init_SPI(clock_freq_level=clock_freq_level, is_MSB=is_MSB, mode=mode,
                              write_read_interval=write_read_interval, CS1_high=CS1_high, CS2_high=CS2_high,
                              is_16bits=is_16bits)

    def write_CS1(self, data: (list, bytes), keep_cs_active: bool = False) -> int:
        """
        Write data to SPI bus with CS1 activated
        :param data: max length up to 32768 bytes at one time
        :type data: :obj:`list`, :obj:`bytes`
        :param keep_cs_active: keep CS pin active after sending messages
        :type keep_cs_active: bool
        :return: length of sent data
        :rtype: int
        """
        if self.dev.CS2_enabled:
            # deactivate CS2 if activated
            self.dev.set_CS2(False)

        if not self.dev.CS1_enabled:
            # activate CS1 if not
            self.dev.set_CS1(True)

        ret = self.dev.spi_write(bytes(data))

        if not keep_cs_active:
            self.dev.set_CS1(False)

        return ret

    def read_CS1(self, length: int, keep_cs_active: bool = False) -> list:
        """
        Read data from SPI bus with CS1 activated and return list of bytes received
        :param length: length of data to read
        :type length: int
        :param keep_cs_active: keep CS pin active after sending messages
        :type keep_cs_active: bool
        :return: list of bytes received
        :rtype: list
        """
        if self.dev.CS2_enabled:
            # deactivate CS2 if activated
            self.dev.set_CS2(False)

        if not self.dev.CS1_enabled:
            # activate CS1 if not
            self.dev.set_CS1(True)

        ret = self.dev.spi_read(length)

        if not keep_cs_active:
            self.dev.set_CS1(False)

        return ret

    def writeRead_CS1(self, data: (list, bytes), keep_cs_active: bool = False) -> list:
        """
        Write and read data through SPI bus with CS1 activated and return list of bytes
        :param data: data to write
        :type data: :obj:`list`, :obj:`bytes`
        :param keep_cs_active: keep CS1 pin active after sending messages
        :type keep_cs_active: bool
        :return: list of bytes received
        :rtype: list
        """
        if self.dev.CS2_enabled:
            # deactivate CS2 if activated
            self.dev.set_CS2(False)

        if not self.dev.CS1_enabled:
            # activate CS1 if not
            self.dev.set_CS1(True)

        ret = self.dev.spi_read_write(data)

        if not keep_cs_active:
            self.dev.set_CS1(False)

        return ret

    def write_CS2(self, data: (list, bytes), keep_cs_active: bool = False) -> int:
        """
        Write data to SPI bus with CS2 activated
        :param data: max length up to 32768 bytes at one time
        :type data: :obj:`list`, :obj:`bytes`
        :param keep_cs_active: bool, keep CS pin active after sending messages
        :type keep_cs_active: bool
        :return: length of sent data
        :rtype: int
        """
        if self.dev.CS1_enabled:
            # deactivate CS1 if activated
            self.dev.set_CS1(False)

        if not self.dev.CS2_enabled:
            # activate CS2 if not
            self.dev.set_CS2(True)

        ret = self.dev.spi_write(bytes(data))

        if not keep_cs_active:
            self.dev.set_CS2(False)

        return ret

    def read_CS2(self, length: int, keep_cs_active: bool = False) -> list:
        """
        Read data from SPI bus with CS2 activated and return list of bytes received
        :param length: length of data to read
        :type length: intr sending messages
        :type keep_cs_active: bool
        :param keep_cs_active: keep CS pin active afte
        :return: list of bytes received
        :rtype: list
        """
        if self.dev.CS1_enabled:
            # deactivate CS1 if activated
            self.dev.set_CS1(False)

        if not self.dev.CS2_enabled:
            # activate CS2 if not
            self.dev.set_CS2(True)

        ret = self.dev.spi_read(length)

        if not keep_cs_active:
            self.dev.set_CS2(False)

        return ret

    def writeRead_CS2(self, data: (list, bytes), keep_cs_active: bool = False) -> list:
        """
        Write and read data through SPI bus with CS2 activated and return list of bytes
        :param data: data to write
        :type data: :obj:`list`, :obj:`bytes`
        :param keep_cs_active: keep CS1 pin active after sending messages
        :type keep_cs_active: bool
        :return: list of bytes received
        :rtype: list
        """
        if self.dev.CS1_enabled:
            # deactivate CS1 if activated
            self.dev.set_CS1(False)

        if not self.dev.CS2_enabled:
            # activate CS2 if not
            self.dev.set_CS2(True)

        ret = self.dev.spi_read_write(data)

        if not keep_cs_active:
            self.dev.set_CS2(False)

        return ret
