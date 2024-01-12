#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: i2cy(i2cy@outlook.com)
# Project: CH347-HIDAPI
# Filename: uart
# Created on: 2024/1/8

from .__device import CH347HIDUART1
import threading
import time


class UARTDevice:

    def __init__(self, baudrate: int = 115200, stop_bits: int = 1, verify_bits: int = 0, timeout: int = 32,
                 multithreading: bool = True):
        """
        Initialize the configuration of the UART interface
        :param baudrate: the baudrate of the device, default is 115200, (Min: 1200, Max: 9M)
        :type baudrate: int
        :param stop_bits: number of stop bits, default is 1
        :type stop_bits: int
        :param verify_bits: number of verify bits, default is 0
        :type verify_bits: int
        :param timeout: timeout in milliseconds, default is 32, this value should not exceed the maximum of 255
        :type timeout: int
        :param multithreading: whether to use multithreading to receive the data in parallel, default is True
        :type multithreading: bool
        """
        self.dev = CH347HIDUART1()
        self.__multithreading = False
        status = self.dev.init_UART(baudrate=baudrate, stop_bits=stop_bits, verify_bits=verify_bits, timeout=timeout)
        if not status:
            raise Exception("failed to initialize UART-1 interface on CH347")

        self.__multithreading = multithreading

        self.__received_data = []
        self.__live = True
        self.__thread = threading.Thread(target=self.__receiver_thread)
        self.__data_lock = threading.Lock()

        if self.__multithreading:
            # enable multithreading receiver
            self.__thread.start()

    def __receiver_thread(self):
        """
        Receive data from the UART interface and put it in a queue to store the received data
        :return:
        """
        while self.__live:
            data = self.dev.read_raw()
            if data:
                self.__data_lock.acquire()
                # print("received data:", bytes(data).hex())
                self.__received_data.extend(data)
                self.__data_lock.release()
            else:
                time.sleep(0.01)

    def __del__(self) -> None:
        if self.__multithreading:
            self.__live = False
            try:
                self.__data_lock.release()
                self.__thread.join()
            except RuntimeError:
                pass

    def kill(self):
        """
        Kill receiver thread if multithreading is on
        :return:
        """
        if self.__multithreading:
            self.__live = False
            try:
                self.__data_lock.release()
                self.__thread.join()
            except RuntimeError:
                pass

    def write(self, data: bytes) -> int:
        """
        Write data to the device
        :param data: data to write
        :type data: bytes
        :return: wrote length
        :rtype: int
        """
        return self.dev.write_raw(data)

    def read(self, length: int = -1, timeout: int = 5) -> list:
        """
        Read data from the device if any byte is available
        :param length: maximum length of the data, default is -1 which means read all bytes that received
        :type length: int
        :param timeout: timeout in seconds, default is 5, set to 0 means return data from buffer immediately instead of
        waiting for the buffer to collect enough data (available only for multithreading)
        :type timeout: int
        :return: list of bytes read
        :rtype: list
        """
        if self.__multithreading:
            # wait for data
            t0 = time.time()

            if length < 0:
                while time.time() - t0 < timeout and len(self.__received_data) == 0:
                    time.sleep(0.002)
            else:
                while time.time() - t0 < timeout and length > len(self.__received_data):
                    time.sleep(0.002)

            self.__data_lock.acquire()

            if len(self.__received_data) > length > 0:
                ret = self.__received_data[:length]
                self.__received_data = self.__received_data[length:]

            else:
                ret = self.__received_data
                self.__received_data = []

            self.__data_lock.release()

        else:
            ret = self.dev.read_raw(length)

        return ret
