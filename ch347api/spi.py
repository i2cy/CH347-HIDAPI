#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: i2cy(i2cy@outlook.com)
# Project: CH347PythonLib
# Filename: hid
# Created on: 2022/11/11

import hid
import time
import struct

VENDOR_ID = 6790
PRODUCT_ID = 21980


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
        self.write(b"\x00\x04\x00\xca\x01\x00\x01\x00")  # reset device
        self.read(64)
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


if __name__ == '__main__':
    import random
    from hashlib import sha256

    """
    Tests below requires MOSI-MISO short connected (outer-loop)
    """


    def generate_random_data(length=50):
        # generate test bytes for transmission
        res = []
        for i in range(length):
            res.append(int(random.random() * 255))
        return bytes(res)


    # initialize a new CH347HIDDev device object
    test_dev = CH347HIDDev(VENDOR_ID, PRODUCT_ID, 1)

    # print HID device information
    print("Manufacturer: %s" % test_dev.get_manufacturer_string())
    print("Product: %s" % test_dev.get_product_string())
    print("Serial No: %s" % test_dev.get_serial_number_string())

    # initialize SPI settings
    test_dev.init_SPI(0, mode=3)  # CLK speed: 60Mhz, SPI mode: 0b11
    test_dev.set_CS1()  # enable CS1 for transmission

    test_data_frame_length = 32768
    time.sleep(0.2)

    input("(press ENTER to perform test)")

    # generate test bytes
    data = generate_random_data(test_data_frame_length)

    # write A5 5A 5A A5 through API
    test_dev.spi_write(b"\xa5\x5a\x5a\xa5")

    # read & write test
    print("performing spi_read_write test...")
    feed = test_dev.spi_read_write(data)
    print("R/W loop accusation test result: {}".format(bytes(feed) == data))

    # specialized speed test (for project)
    t0 = time.time()
    for ele in range(4 * 3 * 200_000 // test_data_frame_length + 1):
        feed = test_dev.spi_read(test_data_frame_length)
    print("1 sec of gtem data trans time spent {:.2f} ms".format((time.time() - t0) * 1000))

    test_dev.close()
