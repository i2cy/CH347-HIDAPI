#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: i2cy(i2cy@outlook.com)
# Project: CH347-HIDAPI
# Filename: demo_2
# Created on: 2024/1/7


import random
import time
from ch347api import CH347HIDDev, I2CDevice, SPIDevice, SPIClockFreq, I2CClockFreq


def i2c_demo():
    # initialize an i2c communication object (MPU6050 I2C address: 0x68)
    # -*- Way 1 -*-
    i2c = I2CDevice(addr=0x68)

    # -*- Way 2 -*-
    # i2c = I2CDevice(addr=0x68, clock_freq_level=I2CClockFreq.f_100K)

    # -*- Way 3 -*- (using one device object to make thread safe)
    # dev = CH347HIDDev()
    # i2c_1 = I2CDevice(addr=0x68, ch347_device=dev)
    # i2c_2 = I2CDevice(addr=0x23, ch347_device=dev)
    # i2c_3 = I2CDevice(addr=0x22, ch347_device=dev)

    # read MPU6050 factory data
    d = i2c.read(0x75, 1)
    print("[I2C] read from MPU6050 register 0x75 (should be 0x68): 0x{}".format(d.hex()))

    # reset MPU6050
    status = i2c.write(0x6b, 0x80)
    print("[I2C] write to MPU6050 register 0x6B with data 0x80 to reset the device, status: {}".format(status))
    time.sleep(0.1)

    # setting up MPU6050
    status = i2c.write(0x6b, 0x01)
    print("[I2C] write to MPU6050 register 0x6B with data 0x01, status: {}".format(status))
    status = i2c.write(0x6c, 0x00)
    print("[I2C] write to MPU6050 register 0x6C with data 0x00, status: {}".format(status))
    status = i2c.write(0x19, 0x00)
    print("[I2C] write to MPU6050 register 0x19 with data 0x00, status: {}".format(status))
    status = i2c.write(0x1a, 0x02)
    print("[I2C] write to MPU6050 register 0x1a with data 0x02, status: {}".format(status))
    status = i2c.write(0x1c, 0x08)
    print("[I2C] write to MPU6050 register 0x1c with data 0x08, status: {}".format(status))


def spi_demo():
    # initialize a spi communication object
    # -*- Way 1 -*-
    # spi = SPIDevice()

    # -*- Way 2 -*-:
    spi = SPIDevice(clock_freq_level=SPIClockFreq.f_30M)

    # -*- Way 3 -*- (using one device object to make thread safe):
    # dev = CH347HIDDev()
    # spi = SPIDevice(ch347_device=dev)
    # i2c = I2CDevice(addr=0x68, ch347_device=dev)

    # write test (activate CS -> write data -> deactivate CS)
    print("performing SPI write test")
    spi.write_CS1(b"hello world")
    spi.write_CS2(b"this is ch347")
    spi.write_CS1([0, 1, 2, 3])
    spi.write_CS2([252, 253, 254, 255])

    # write test (activate CS -> write data -> write data -> deactivate CS)
    spi.write_CS1(b"hello world", keep_cs_active=True)
    spi.write_CS1(b"this is ch347")

    # read test (activate CS -> read data -> deactivate CS)
    print("performing SPI read test")
    print("received 16 bytes from SPI bus on CS1:", bytes(spi.read_CS1(16)))

    # write&read test (activate CS -> read data -> deactivate CS)
    random_bytes = random.randbytes(512)
    print("write read test result (with MOSI, MISO short connected): {}".format(
        bytes(spi.writeRead_CS1(random_bytes)) == random_bytes
    ))


if __name__ == "__main__":
    i2c_demo()
    spi_demo()
