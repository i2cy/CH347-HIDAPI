#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: i2cy(i2cy@outlook.com)
# Project: CH347-HIDAPI
# Filename: demo_2
# Created on: 2024/1/7


import random
import time
from ch347api import CH347HIDDev, I2CDevice, SPIDevice, UARTDevice, SPIClockFreq, I2CClockFreq


def i2c_demo():
    print('[I2C] Scan start...')
    hiddev = CH347HIDDev()
    hiddev.init_I2C()
    print('      ' + ''.join(map(lambda a : '{:02X} '.format(a), range(16))))
    for i in range(128):
        if i % 16 == 0:
            print('0x{:02X}: '.format(i), end='')
        exists = hiddev.i2c_exists(i)
        if exists:
            print('{:02X} '.format(i), end='')
        else:
            print('__ ', end='')
        if i % 16 == 15:
            print()
    
    print('[I2C] MPU6050 example')
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
    spi = SPIDevice(clock_freq_level=SPIClockFreq.f_30M, is_16bits=False)

    # -*- Way 3 -*- (using one device object to make thread safe):
    # dev = CH347HIDDev()
    # spi = SPIDevice(ch347_device=dev)
    # i2c = I2CDevice(addr=0x68, ch347_device=dev)

    # write test (activate CS -> write data -> deactivate CS)
    print("[SPI] performing SPI write test")
    spi.write_CS1(b"hello world")
    spi.write_CS2(b"this is ch347")
    spi.write_CS1([0, 1, 2, 3])
    spi.write_CS2([252, 253, 254, 255])

    # write test (activate CS -> write data -> write data -> deactivate CS)
    spi.write_CS1(b"hello world", keep_cs_active=True)
    spi.write_CS1(b"this is ch347")

    # read test (activate CS -> read data -> deactivate CS)
    print("[SPI] performing SPI read test")
    read_length = 32768
    for i in range(2048):
        ret = bytes(spi.read_CS1(read_length))
    print(f"[SPI] received {read_length} bytes from SPI bus on CS1: {ret[:16]}...(total: {len(ret)} bytes)", )

    # write&read test (activate CS -> read data -> deactivate CS)
    random_bytes = b"\xa5\x5a\x5a\xa5" * 128
    print("[SPI] write read test result (with MOSI, MISO short connected): {}".format(
        bytes(spi.writeRead_CS1(random_bytes)) == random_bytes
    ))


def uart_demo():
    # while performing this test please make sure TX and RX pin short connected

    # initialize an uart communication object
    # -*- Way 1 -*-
    uart = UARTDevice(baudrate=7_500_000)

    # -*- Way 2 -*- (with no multithreading receiver)
    # uart = UARTDevice(baudrate=115200, stop_bits=1, verify_bits=0, timeout=128, multithreading=False)

    # uart write test
    test_b1 = b"hello world, this is ch347. "
    test_b2 = b"using CH347-HIDAPI"
    test_b3 = b"\xa5\x5a\x5a\xa5\x00\x01\x02\x03\xfc\xfd\xfe\xff\xa5\x5a\x5a\xa5"
    wrote = uart.write(test_b1)
    print("[UART] wrote {} bytes with content \"{}\"".format(wrote, test_b1.decode("utf-8")))
    wrote = uart.write(test_b2)
    print("[UART] wrote {} bytes with content \"{}\"".format(wrote, test_b2.decode("utf-8")))

    # uart read test
    # time.sleep(0.2)
    read = uart.read(len(test_b1 + test_b2))
    print("[UART] read {} bytes of data test result: {}".format(len(read), bytes(read) == test_b1 + test_b2))
    print("[UART] received: {}".format(bytes(read)))

    # uart accuracy test
    print("[UART] continuous sending and receiving test with 4MB size in progress..")
    payload = test_b3 * 64 * 1024 * 4
    t0 = time.time()
    uart.write(payload)
    read = uart.read(len(payload), timeout=15)
    print("[UART] 4MB payload received, time spent: {:.2f} ms, accuracy test result: {}".format(
        (time.time() - t0) * 1000, bytes(read) == payload))

    # [VITAL] kill sub-thread(receiver thread) for safe exit
    uart.kill()


if __name__ == "__main__":
    #i2c_demo()
    spi_demo()
    #uart_demo()
