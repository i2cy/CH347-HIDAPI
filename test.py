#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: i2cy(i2cy@outlook.com)
# Project: CH347PythonLib
# Filename: test
# Created on: 2023/7/31
import struct

import random
import time
from hashlib import sha256
from ch347api import CH347HIDDev, VENDOR_ID, PRODUCT_ID


def generate_random_data(length=50):
    # generate test bytes for transmission
    res = []
    for i in range(length):
        res.append(int(random.random() * 255))
    return bytes(res)


"""
Tests below requires MOSI-MISO short connected (outer-loop)
"""

if __name__ == '__main__':

    # initialize a new CH347HIDDev device object
    test_dev = CH347HIDDev(VENDOR_ID, PRODUCT_ID, 1)

    # print HID device information
    print("Manufacturer: %s" % test_dev.get_manufacturer_string())
    print("Product: %s" % test_dev.get_product_string())
    print("Serial No: %s" % test_dev.get_serial_number_string())

    # -*- [ i2c test ] -*-

    # initialize I2C with speed 400KHz
    test_dev.init_I2C(2)

    input("(press ENTER to perform I2C test)")

    # write 0x75 to device with address 0x68
    print("I2C test address 0x68")
    status = test_dev.i2c_write(0x68, 0x75)
    print("I2C write 0x75 test: {}".format(status))

    # read 2 bytes from device with address 0x68
    status, feedback = test_dev.i2c_read(0x68, 2)
    print("I2C read 2 bytes test: {}, {}".format(status, feedback.hex()))

    # read 1 byte of register 0x75 from device with address 0x68
    status, feedback = test_dev.i2c_read(0x68, 1, 0x75)
    print("I2C read 1 byte with register address 0x75 test: {}, {}".format(status, feedback.hex()))

    # read 2 bytes of register 0x74 from device with address 0x68
    status, feedback = test_dev.i2c_read(0x68, 2, b"\x74")
    print("I2C read 2 bytes with register address 0x74 test: {}, {}".format(status, feedback.hex()))

    input("(press ENTER to perform SPI test)")

    # initialize SPI settings
    test_dev.init_SPI(0, mode=1)  # CLK speed: 60Mhz, SPI mode: 0b11
    test_dev.set_CS1()  # enable CS1 for transmission

    test_data_frame_length = 32768
    time.sleep(0.2)

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
