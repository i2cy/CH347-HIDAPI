#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: i2cy(i2cy@outlook.com)
# Project: CH347PythonLib
# Filename: hid
# Created on: 2022/11/11


class SPIClockFreq:
    f_60M = 0
    f_30M = 1
    f_15M = 2
    f_7M5 = 3
    f_3M75 = 4
    f_1M875 = 5
    f_937K5 = 6
    f_468K75 = 7


class SPIConfig(list):

    def __init__(self):
        super(SPIConfig, self).__init__(
            b"\x00\x1d\x00\xc0\x1a\x00\x00\x00"
            b"\x04\x01\x00\x00\x02\x00\x01\x00"
            b"\x00\x02\x08\x00\x00\x00\x07\x00"
            b"\x00\x00\xff\x00\x00\x00\x00\x00"
        )

    def as_bytes(self):
        return bytes(self)

    def set_mode(self, mode: int):
        """
        set SPI mode
        :param mode: int, can only be 0, 1, 2, 3
        :return: None
        """
        if mode == 0:
            self[12:16] = b"\x00\x00\x00\x00"
        elif mode == 1:
            self[12:16] = b"\x00\x00\x01\x00"
        elif mode == 2:
            self[12:16] = b"\x02\x00\x00\x00"
        elif mode == 3:
            self[12:16] = b"\x02\x00\x01\x00"
        else:
            raise Exception("SPI mode value needs to be one of 0-3")

    def set_clockSpeed(self, speed_ind: int):
        """
        set SPI clock speed, 0=60MHz, 1=30MHz, 2=15MHz, 3=7.5MHz, 4=3.75MHz, 5=1.875MHz, 6=937.5KHz，7=468.75KHz
        :param speed_ind: int, 0, 1, 2, 3, 4, 5, 6, 7
        :return: None
        """
        if speed_ind == 0:
            self[18] = 0x00
        elif speed_ind == 1:
            self[18] = 0x08
        elif speed_ind == 2:
            self[18] = 0x10
        elif speed_ind == 3:
            self[18] = 0x18
        elif speed_ind == 4:
            self[18] = 0x20
        elif speed_ind == 5:
            self[18] = 0x28
        elif speed_ind == 6:
            self[18] = 0x30
        elif speed_ind == 7:
            self[18] = 0x38
        else:
            raise Exception("SPI mode value needs to be one of 0-7")

    def set_MSB(self, is_msb: bool = False):
        """
        set SPI MSB
        :param is_msb: bool
        :return: None
        """
        if is_msb:
            self[20] = 0x00
        else:
            self[20] = 0x80

    def set_writeReadInterval(self, us: int):
        """
        set SPI write read interval value
        :param us: int, 0-65535
        :return: None
        """
        self[24:26] = us.to_bytes(2, "little", signed=False)

    def set_CS1Polar(self, high: bool = False):
        """
        set SPI CS1 port polarity, high or low
        :param high: bool
        :return: None
        """
        if high:
            self[27] |= 0x80
        else:
            self[27] &= 0x7f

    def set_CS2Polar(self, high: bool = False):
        """
        set SPI CS2 port polarity, high or low
        :param high: bool
        :return: None
        """
        if high:
            self[27] |= 0x40
        else:
            self[27] &= 0xbf


class CSConfig(list):

    def __init__(self):
        super(CSConfig, self).__init__(
            b"\x00\x0d\x00\xc1\x0a\x00\xc0\x00"
            b"\x00\x00\x00\x00\x00\x00\x00\x00"
            b"\x00\x00\x00\x00\x00\x00\x00\x00"
            b"\x00\x00\x00\x00\x00\x00\x00\x00"
        )
        self.active_delay_us = 0
        self.deactive_delay_us = 0

    def as_bytes(self) -> bytes:
        """
        export data list as bytes
        :return: bytes
        """
        return bytes(self)

    def set_CS1Enable(self, enable: bool = True):
        """
        set Chip-Select pin 1 enable
        :param enable: bool, default = True
        :return: None
        """
        if enable:
            self[5:32] = b"\x00\x80" + \
                         self.active_delay_us.to_bytes(2, "little", signed=False) + \
                         self.deactive_delay_us.to_bytes(2, "little", signed=False) + \
                         b"\x00" * 5
        else:
            self[5:32] = b"\x00\xc0" + \
                         self.active_delay_us.to_bytes(2, "little", signed=False) + \
                         self.deactive_delay_us.to_bytes(2, "little", signed=False) + \
                         b"\x00" * 5

    def set_CS2Enable(self, enable: bool = True):
        """
        set Chip-select pin 2 enable
        :param enable: bool, default = True
        :return: None
        """
        if enable:
            self[5:32] = b"\x00" * 5 + b"\x00\x80" + \
                         self.active_delay_us.to_bytes(2, "little", signed=False) + \
                         self.deactive_delay_us.to_bytes(2, "little", signed=False)
        else:
            self[5:32] = b"\x00" * 5 + b"\x00\xc0" + \
                         self.active_delay_us.to_bytes(2, "little", signed=False) + \
                         self.deactive_delay_us.to_bytes(2, "little", signed=False)

    def set_activeDelay(self, us: int):
        """
        set the delay time(us) from CS enabled to actually start transmitting
        :param us: int
        :return: None
        """
        self.active_delay_us = us

    def set_deactivateDelay(self, us: int):
        """
        set the delay time(us) before deactivate CS
        :param us: int
        :return: None
        """
        self.deactive_delay_us = us
