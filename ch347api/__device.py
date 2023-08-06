#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: i2cy(i2cy@outlook.com)
# Project: CH347PythonLib
# Filename: device
# Created on: 2023/7/31


import hid
import struct
from .__spi import CSConfig, SPIConfig
from .__i2c import convert_i2c_address, convert_int_to_bytes
from typing import Tuple, Any

VENDOR_ID: int = 6790
PRODUCT_ID: int = 21980


class CH347HIDDev(hid.device):

    def __init__(self, vendor_id, product_id, interface_num):
        """
        Class of CH347 device based on hidapi
        :param vendor_id: int
        :param product_id: int
        :param interface_num: int
        """
        super(CH347HIDDev, self).__init__()
        target = None
        for ele in hid.enumerate():
            if ele["vendor_id"] == vendor_id and ele["product_id"] == product_id:
                if ele['interface_number'] == interface_num:
                    target = ele['path']
        self.open_path(target)

        self.CS1_enabled = False
        self.CS2_enabled = False
        self.cs_activate_delay = 0
        self.cs_deactivate_delay = 0
        self.i2c_initiated = False

    def reset(self):
        """
        reset device
        :return:
        """
        self.write(b"\x00\x04\x00\xca\x01\x00\x01\x00")  # reset device
        self.read(64)

    # --*-- [ I2C ] --*--
    def init_I2C(self, clock_speed_level: int = 1):
        """
        initialize I2C configuration
        :param clock_speed_level: int, 0-20KHz, 1-100KHz, 2-400KHz, 3-750KHz
        :return: None
        """
        self.write(struct.pack("<BHBB", 0x00, 3, 0xaa, 0x60 | clock_speed_level))
        self.i2c_initiated = True

    def i2c_write(self, addr: (int, bytes), data: (int, bytes)) -> bool:
        """
        write data through I2C bus using 7-bits address
        :param addr: Any[int, bytes], 7-bits of device address
        :param data: Any[int, bytes], one byte or several bytes of data to send (62 bytes max),
        this method will automatically convert it into bytes with byte order 'big' unsigned if data type is int,
        e.g. 0x00f1f2 -> b'\xf1\xf2'
        :return: bool, operation status
        """
        # convert address
        addr = convert_i2c_address(addr, read=False)

        # convert data
        data = convert_int_to_bytes(data)

        # assemble i2c frame
        payload = addr + data
        # send data through i2c stream
        status, feedback = self.i2c_read_write_raw(payload)

        return status

    def i2c_read(self, addr: (int, bytes), read_length: int,
                 register_addr: (int, bytes) = None) -> Tuple[bool, bytes]:
        """
        read byte(s) data from i2c bus with register address using 7-bits of device address
        :param addr: Any[int, bytes], 7-bits of device address
        :param read_length: int, length
        :param register_addr: Optional[int, bytes], one byte or several bytes of address of register,
        this method will automatically convert it into bytes with byte order 'big' unsigned if data type is int,
        e.g. 0x00f1f2 -> b'\xf1\xf2'
        :return: Tuple[operation_status bool, feedback bytes]
        """
        # convert address
        if register_addr is None:
            register_addr = b""
            # convert address with reading signal
            addr = convert_i2c_address(addr, read=True)

        else:
            register_addr = convert_int_to_bytes(register_addr)
            # convert address with writing signal
            addr = convert_i2c_address(addr, read=False)

        # assemble payload
        payload = addr + register_addr

        # send and receive data from i2c bus
        status, feedback = self.i2c_read_write_raw(payload, read_len=read_length)

        return status, feedback

    def i2c_read_write_raw(self, data: bytes, read_len: int = 0) -> Tuple[bool, bytes]:
        """
        read and write i2c bus through I2CStream
        :param read_len: int, length of data to read (max 63B)
        :param data: bytes
        :return: tuple(<bool status>, <bytes feedback>)
        """
        if not self.i2c_initiated:
            raise Exception('I2C device initialization required')

        if read_len == 0:
            tail = b"\x75"
        elif read_len == 1:
            tail = b"\xc0\x75"
            if len(data) > 1:
                tail = b"\x74\x81\xd1" + tail
        elif read_len < 64:
            tail = struct.pack("<bBB", -65 + read_len, 0xc0, 0x75)
            if len(data) > 1:
                tail = b"\x74\x81\xd1" + tail
        else:
            raise Exception("read length exceeded max size of 63 Bytes")
        payload = struct.pack("<BHBBB", 0x00, len(data) + len(tail) + 4, 0xaa, 0x74, len(data) | 0b1000_0000)
        payload += data + tail

        self.write(payload)

        feedback = bytes(self.read(512))
        payload_length = struct.unpack("<H", feedback[:2])[0]
        ack_stops = len(data) + bool(read_len) + 2
        if len(data) == 1:
            ack_stops -= 1
        ack_signals = feedback[2:ack_stops]
        payload = feedback[ack_stops: payload_length + 2]
        # print("i2c package received:", feedback)
        print("i2c feedback payload length: {}, acks: {}, content: {}".format(payload_length, ack_signals,
                                                                              feedback[:payload_length + 2]))

        return sum(ack_signals) == len(ack_signals), payload

    # --*-- [ SPI ] --*--
    def init_SPI(self, clock_speed_level: int = 1, is_MSB: bool = True,
                 mode: int = 3, write_read_interval: int = 0,
                 CS1_high: bool = False,
                 CS2_high: bool = False):
        """
        initialize SPI configuration
        :param clock_speed_level: int, 0-7
        :param is_MSB: bool
        :param mode: int, 0-3
        :param write_read_interval: int, 0-65535
        :param CS1_high: bool
        :param CS2_high: bool
        :return:
        """
        self.CS1_enabled = False
        self.CS2_enabled = False
        conf = SPIConfig()
        conf.set_mode(mode)
        conf.set_clockSpeed(clock_speed_level)
        conf.set_MSB(is_MSB)
        conf.set_writeReadInterval(write_read_interval)
        conf.set_CS1Polar(CS1_high)
        conf.set_CS2Polar(CS2_high)
        self.write(conf)
        self.read(64)

    def set_CS1(self, enable: bool = True, active_delay_us: int = -1,
                deactivate_delay_us: int = -1):
        """
        set CS1 enable/disable with delay settings
        :param enable: bool
        :param active_delay_us: int
        :param deactivate_delay_us: int
        :return:
        """
        if enable and self.CS2_enabled:
            self.set_CS2(enable=False)
        if active_delay_us >= 0:
            self.cs_activate_delay = active_delay_us
        if deactivate_delay_us >= 0:
            self.cs_deactivate_delay = deactivate_delay_us
        conf = CSConfig()
        conf.set_activeDelay(self.cs_activate_delay)
        conf.set_deactivateDelay(self.cs_deactivate_delay)
        conf.set_CS1Enable(enable)
        self.write(conf)
        if enable:
            self.CS1_enabled = True
            self.CS2_enabled = False
        else:
            self.CS1_enabled = False
            self.CS2_enabled = False

    def set_CS2(self, enable: bool = True, active_delay_us: int = -1,
                deactivate_delay_us: int = -1):
        """
        set CS2 enable/disable with delay settings
        :param enable: bool
        :param active_delay_us: int
        :param deactivate_delay_us: int
        :return:
        """
        if enable and self.CS1_enabled:
            self.set_CS1(enable=False)
        if active_delay_us >= 0:
            self.cs_activate_delay = active_delay_us
        if deactivate_delay_us >= 0:
            self.cs_deactivate_delay = deactivate_delay_us
        conf = CSConfig()
        conf.set_activeDelay(self.cs_activate_delay)
        conf.set_deactivateDelay(self.cs_deactivate_delay)
        conf.set_CS2Enable(enable)
        self.write(conf)
        if enable:
            self.CS2_enabled = True
            self.CS1_enabled = False
        else:
            self.CS1_enabled = False
            self.CS2_enabled = False

    def spi_write(self, data: bytes) -> int:
        """
        write data to SPI devices
        :param data: bytes, max length up to 32768 bytes
        :return: int, length of sent data
        """
        if not (self.CS1_enabled or self.CS2_enabled):
            raise Exception("no CS enabled yet")

        length = len(data)
        if length > 32768:
            # exceeded max package size
            raise Exception("package size {} exceeded max size of 32768 Bytes".format(length))

        raw = struct.pack("<BHBH", 0x00, length + 3, 0xc4, length) + data
        self.write(raw)
        self.read(64)

        return length

    def spi_read_write(self, data: bytes) -> list:
        """
        write data to SPI devices
        :param data: bytes, max length up to 32768 bytes
        :return: int, length of sent data
        """
        if not (self.CS1_enabled or self.CS2_enabled):
            raise Exception("no CS enabled yet")

        length = len(data)
        if length > 32768:
            # exceeded max package size
            raise Exception("package size {} exceeded max size of 32768 Bytes".format(length))

        sent = 0
        while sent < length:
            left = length - sent
            if left >= 507:
                frame_payload_length = 507
            else:
                frame_payload_length = left
            raw = struct.pack("<BHBH", 0x00, frame_payload_length + 3, 0xc2, frame_payload_length) + \
                  data[sent:sent + frame_payload_length]
            sent += frame_payload_length
            self.write(raw)

        ret = []
        while len(ret) < length:
            frame = self.read(512)
            frame_len, cmd_id, payload_len = struct.unpack("<HBH", bytes(frame[:5]))
            ret += frame[5:5 + payload_len]

        return ret

    def spi_read(self, length) -> list:
        """
        read data from SPI device with given length
        :param length: int
        :return:
        """
        if not (self.CS1_enabled or self.CS2_enabled):
            raise Exception("no CS enabled yet")

        if length > 32768:
            # exceeded max package size
            raise Exception("package size {} exceeded max size of 32768 Bytes".format(length))

        raw = struct.pack("<BHBHL", 0x00, 7, 0xc3, 4, length)
        self.write(raw)

        ret = []
        while len(ret) < length:
            frame = self.read(512)
            frame_len, cmd_id, payload_len = struct.unpack("<HBH", bytes(frame[:5]))
            ret += frame[5:5 + payload_len]

        return ret
