#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: i2cy(i2cy@outlook.com)
# Project: CH347PythonLib
# Filename: device
# Created on: 2023/7/31
import time

import hid
import struct
from .__spi import CSConfig, SPIConfig
from .__i2c import convert_i2c_address, convert_int_to_bytes
from typing import Tuple, Any
from functools import wraps
import warnings

VENDOR_ID: int = 6790
PRODUCT_ID: int = 21980


class CH347HIDUART1(hid.device):

    def __init__(self, vendor_id=VENDOR_ID, product_id=PRODUCT_ID):
        """
        Class of CH347 UART1 interface based on hidapi
        :param vendor_id: the vender ID of the device
        :type vendor_id: int
        :param product_id: the product ID of the device
        :type product_id: int
        """
        super(CH347HIDUART1, self).__init__()
        target = None
        for ele in hid.enumerate():
            if ele["vendor_id"] == vendor_id and ele["product_id"] == product_id:
                if ele['interface_number'] == 0:  # UART interface ID: 0
                    target = ele['path']

        self.open_path(target)

    def init_UART(self, baudrate: int = 115200, stop_bits: int = 1, verify_bits: int = 0, timeout: int = 32) -> bool:
        """
        Initialize the configuration of the UART interface
        :param baudrate: the baudrate of the device, default is 115200
        :type baudrate: int
        :param stop_bits: number of stop bits, default is 1
        :type stop_bits: int
        :param verify_bits: number of verify bits, default is 0
        :type verify_bits: int
        :param timeout: timeout in milliseconds, default is 32, this value should not exceed the maximum of 255
        :type timeout: int
        :return: operation status
        :rtype: bool
        """
        header = b"\x00\xcb\x08\x00"
        stop_bits = stop_bits * 2 - 2

        if baudrate < 1200 or baudrate > 7_500_000:
            raise ValueError("Invalid baudrate, correct value should ranging from 1200 to 7500000")

        if timeout > 255:
            raise Exception("timeout should not exceed the maximum number of 255")

        payload = header + struct.pack("<IBBBB", baudrate, stop_bits, verify_bits, 0x08, timeout)
        response = bool(self.send_feature_report(payload))

        # response = self.get_feature_report(0, 16)
        return response

    def write_raw(self, data: bytes) -> int:
        """
        Write data to the device
        :param data: data to write
        :type data: bytes
        :return: wrote length
        :rtype: int
        """
        offset = 0
        while len(data) - offset > 510:
            payload = struct.pack("<BH", 0x00, 510) + data[offset:offset + 510]
            self.write(payload)
            offset += 510
        payload = struct.pack("<BH", 0x00, len(data) - offset) + data[offset:len(data)]
        self.write(payload)
        offset += len(data) - offset

        return offset

    def read_raw(self, length: int = -1) -> list:
        """
        Read data from the device if any byte is available
        :param length: maximum length of the data, default is -1 which means read all bytes that received
        :type length: int
        :return: list of bytes read
        :rtype: list
        """
        self.set_nonblocking(1)

        ret = []
        while len(ret) < length or length < 0:
            chunk = self.read(512, timeout_ms=200)
            if chunk:
                chunk_len = struct.unpack("<H", bytes(chunk[0:2]))[0]
                ret.extend(chunk[2:chunk_len+2])
            else:
                break

        self.set_nonblocking(0)

        return ret


class CH347HIDDev(hid.device):

    def __init__(self, vendor_id=VENDOR_ID, product_id=PRODUCT_ID, interface_num=None,
                 enable_device_lock=True, warnings_enabled=True):
        """
        Class of CH347 SPI/I2C/GPIO interface based on hidapi
        :param vendor_id: the vendor ID of the device
        :type vendor_id: int
        :param product_id: the product ID of the device
        :type product_id: int
        :param interface_num: the interface number of the device (deprecated)
        :type interface_num: int
        :param enable_device_lock: whether to enable device in case of multithreading communication
        :type enable_device_lock: bool
        :param warnings: whether to enable warnings output
        :type warnings: bool
        """

        if interface_num is not None and warnings_enabled:
            warnings.warn("interface_num is deprecated and will be removed in future releases."
                          " From now on interface_num will be set automatically to 1",
                          DeprecationWarning)

        super(CH347HIDDev, self).__init__()
        target = None
        for ele in hid.enumerate():
            if ele["vendor_id"] == vendor_id and ele["product_id"] == product_id:
                if ele['interface_number'] == 1:  # SPI/I2C/GPIO interface ID: 1
                    target = ele['path']

        self.open_path(target)

        self.CS1_enabled = False
        self.CS2_enabled = False
        self.cs_activate_delay = 0
        self.cs_deactivate_delay = 0
        self.i2c_initiated = False
        self.spi_initiated = False
        self.lock_enabled = enable_device_lock
        self.is_busy = False
        self.warnings_enabled = warnings

    def __busy_check(self, timeout=5) -> bool:
        """
        Check if device is busy
        :param timeout: time to wait for other thread to reset the busy flag
        :type timeout: int
        :return: busy status
        :rtype: bool
        """
        t0 = time.time()
        while self.lock_enabled and self.is_busy and time.time() - t0 < timeout:
            time.sleep(0.001)

        return self.is_busy

    def __device_lock(timeout: int = 5):
        """
        device lock decorator
        :param timeout: timeout to wait for device to unlock
        :type timeout: int
        :return:
        """

        def aop(func):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                # check busy flag
                self.__busy_check(timeout)
                # set busy flag
                self.is_busy = True
                ret = func(self, *args, **kwargs)
                # unset busy flag
                self.is_busy = False
                return ret

            return wrapper

        return aop

    @__device_lock(2)
    def reset(self):
        """
        reset device
        :return:
        """
        self.write(b"\x00\x04\x00\xca\x01\x00\x01\x00")  # reset device
        self.read(512, timeout_ms=200)

    # --*-- [ I2C ] --*--
    @__device_lock(2)
    def init_I2C(self, clock_freq_level: int = 1):
        """
        initialize I2C configuration
        :param clock_freq_level: 0-20KHz, 1-100KHz, 2-400KHz, 3-750KHz
        :type clock_freq_level: int
        :return:
        """
        self.write(struct.pack("<BHBB", 0x00, 3, 0xaa, 0x60 | clock_freq_level))
        self.i2c_initiated = True

    @__device_lock(2)
    def i2c_write(self, addr: (int, bytes), data: (int, bytes)) -> bool:
        """
        write data through I2C bus using 7-bits address
        :param addr: Any[int, bytes], 7-bits of device address
        :type addr: :obj:`int`, :obj:`bytes`
        :param data: one byte or several bytes of data to send (62 bytes max),
        this method will automatically convert it into bytes with byte order 'big' unsigned if data type is int,
        e.g. 0x00f1f2 -> b'\xf1\xf2'
        :type data: :obj:`int`, :obj:`bytes`
        :return: operation status
        :rtype: bool
        """
        # convert address
        addr = convert_i2c_address(addr, read=False)

        # convert data
        data = convert_int_to_bytes(data)

        # assemble i2c frame
        payload = addr + data
        # send data through i2c stream
        status, feedback = self.__i2c_read_write_raw(payload)

        return status

    @__device_lock(2)
    def i2c_read(self, addr: (int, bytes), read_length: int,
                 register_addr: (int, bytes) = None) -> Tuple[bool, bytes]:
        """
        read byte(s) data from i2c bus with register address using 7-bits of device address
        :param addr: 7-bits of device address
        :type addr: :obj:`int`, :obj:`bytes`
        :param read_length: length of data to read from i2c bus
        :type read_length: int
        :param register_addr: Optional[int, bytes], one byte or several bytes of address of register,
        this method will automatically convert it into bytes with byte order 'big' unsigned if data type is int,
        e.g. 0x00f1f2 -> b'\xf1\xf2'
        :type register_addr: :obj:`int`, :obj:`bytes` (optional)
        :return: Tuple[operation_status bool, feedback bytes]
        :rtype: (bool, bytes)
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
        status, feedback = self.__i2c_read_write_raw(payload, read_len=read_length)

        return status, feedback
    
    def i2c_exists(self, addr: int | bytes) -> bool:
        """
        checks if device responds at given address (useful for I2C scanner)
        :param addr: 7-bits of device address
        :type addr: :obj:`int`, :obj:`bytes`
        :return: bool indicating device available
        :rtype: bool
        """
        addr = convert_i2c_address(addr, read=False)

        _, feedback = self.__i2c_read_write_raw(addr)
        return len(feedback) == 1 and feedback[0] != 0x00


    def __i2c_read_write_raw(self, data: bytes, read_len: int = 0) -> Tuple[bool, bytes]:
        """
        read and write i2c bus through I2CStream
        :param read_len: length of data to read (max 63B)
        :type read_len: int
        :param data: data to write
        :type data: bytes
        :return: tuple(<bool status>, <bytes feedback>)
        :rtype: (:obj:`bool`, :obj:`bytes`)
        """
        if not self.i2c_initiated:
            raise Exception('I2C device initialization required')

        if read_len == 0:
            tail = b"\x75"
        elif read_len == 1:
            tail = b"\xc0\x75"
            if len(data) > 1:
                # Convert write address into read address
                tail = b"\x74\x81" + bytes([data[0] | 0x01]) + tail
        elif read_len < 64:
            tail = struct.pack("<bBB", -65 + read_len, 0xc0, 0x75)
            if len(data) > 1:
                # Convert write address into read address
                tail = b"\x74\x81" + bytes([data[0] | 0x01]) + tail
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
        # print("i2c feedback payload length: {}, acks: {}, content: {}".format(payload_length, ack_signals,
        #                                                                       feedback[:payload_length + 2]))

        return sum(ack_signals) == len(ack_signals), payload

    # --*-- [ SPI ] --*--
    @__device_lock(2)
    def init_SPI(self, clock_freq_level: int = 1, is_MSB: bool = True,
                 mode: int = 0, write_read_interval: int = 0,
                 CS1_high: bool = False,
                 CS2_high: bool = False,
                 is_16bits: bool = False):
        """
        initialize SPI configuration
        :param clock_freq_level: clock freq, 0=60M, 1=30M, 2=15M, 3=7.5M, 4=3.75M, 5=1.875M, 6=937.5K，7=468.75K
        :type clock_freq_level: int
        :param is_MSB: enable MSB mode
        :type is_MSB: bool
        :param mode: int, 0-3
        :type mode: int
        :param write_read_interval: 0-65535
        :type write_read_interval: int
        :param CS1_high: set SPI CS1 port polarity, True=Active-High, False=Active-Low
        :type CS1_high: bool
        :param CS2_high: set SPI CS1 port polarity, True=Active-High, False=Active-Low
        :type CS2_high: bool
        :param is_16bits: enable 16-bits mode
        :type is_16bits: bool
        :return:
        """
        self.CS1_enabled = False
        self.CS2_enabled = False
        conf = SPIConfig()
        conf.set_mode(mode)
        conf.set_clockSpeed(clock_freq_level)
        conf.set_MSB(is_MSB)
        conf.set_writeReadInterval(write_read_interval)
        conf.set_CS1Polar(CS1_high)
        conf.set_CS2Polar(CS2_high)
        conf.set_mode16bits(is_16bits)
        self.write(conf)
        self.read(512, timeout_ms=200)
        self.spi_initiated = True

    @__device_lock(2)
    def set_CS1(self, enable: bool = True, active_delay_us: int = -1,
                deactivate_delay_us: int = -1):
        """
        set CS1 enable/disable with delay settings
        :param enable: enable/disable CS1
        :type enable: bool
        :param active_delay_us: delay for CS1 (in μs) to activate
        :type active_delay_us: int
        :param deactivate_delay_us: delay for CS1 (in ms) to deactivate
        :type deactivate_delay_us: int
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

    @__device_lock(2)
    def set_CS2(self, enable: bool = True, active_delay_us: int = -1,
                deactivate_delay_us: int = -1):
        """
        set CS2 enable/disable with delay settings
        :param enable: enable/disable CS2
        :type enable: bool
        :param active_delay_us: delay for CS2 (in μs) to activate
        :type active_delay_us: int
        :param deactivate_delay_us: delay for CS2 (in μs) to deactivate
        :type deactivate_delay_us: int
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

    @__device_lock(2)
    def spi_write(self, data: bytes) -> int:
        """
        write data to SPI devices
        :param data: max length up to 32768 Bytes
        :type data: bytes
        :return: int, length of sent data
        :rtype: int
        """
        if not (self.CS1_enabled or self.CS2_enabled):
            raise Exception("no CS enabled yet")

        length = len(data)
        if length > 32768:
            # exceeded max package size
            raise Exception("package size {} exceeded max size of 32768 Bytes".format(length))

        raw = struct.pack("<BHBH", 0x00, length + 3, 0xc4, length) + data
        self.write(raw)
        self.read(512, timeout_ms=200)

        return length

    @__device_lock(2)
    def spi_read_write(self, data: bytes) -> list:
        """
        write data to SPI devices
        :param data: bytes, max length up to 32768 bytes
        :type data: bytes
        :return: list of bytes received from SPI device
        :rtype: list
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
            frame = self.read(512, timeout_ms=200)
            if not frame:
                if self.warnings_enabled:
                    warnings.warn("read incomplete, read {} bytes (expecting {} bytes)".format(len(ret), length))
                break
            frame_len, cmd_id, payload_len = struct.unpack("<HBH", bytes(frame[:5]))
            ret += frame[5:5 + payload_len]

        return ret

    @__device_lock(2)
    def spi_read(self, length) -> list:
        """
        read data from SPI device with given length
        :param length: length of data to read (no more than 32768)
        :type length: int
        :return: list of data received from SPI device
        :rtype: list
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
            frame = self.read(512, timeout_ms=200)
            if not frame:
                if self.warnings_enabled:
                    warnings.warn("read incomplete, read {} bytes (expecting {} bytes)".format(len(ret), length))
                break
            frame_len, cmd_id, payload_len = struct.unpack("<HBH", bytes(frame[:5]))
            ret += frame[5:5 + payload_len]

        return ret
