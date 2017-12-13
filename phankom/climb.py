#! /usr/bin/env python
# -*- coding: utf-8 -*-

# *************************************************************
#  Copyright (c) Huoty - All rights reserved
#
#      Author: Huoty <sudohuoty@gmail.com>
#  CreateTime: 2017-10-28 16:57:26
# *************************************************************

"""Climb over the GFW(Great Fire Wall)"""

import os
import socket
import struct
import random
import select

from .socks import Socks5Server
from .crypt import MixCipher
from .utils import affirm, is_even


class BaseClimbServer(Socks5Server):
    """Climb over GFW(Great Fire Wall) server based on Socks"""

    def __init__(self, key, host="0.0.0.0", port=1080):
        self.cipher = MixCipher(key)
        super().__init__(host, port)

    def recv_encrypted_data(self, sock=None):
        sock = sock or self.sock
        head = self.recv_data(sock, 6)
        self.log.debug(head)
        if len(head) <= 0:
            return head
        data_len = (int.from_bytes(head[3:5], byteorder="big")
                    if is_even(head[2]) else
                    int.from_bytes(head[4:], byteorder="big"))
        size = data_len
        data = b''
        while 1:
            data += self.recv_data(sock, size)
            recv_len = len(data)
            if recv_len < data_len:
                size = data_len - recv_len
            elif recv_len == data_len:
                break
            else:
                raise Exception("received data is too long")
        data = self.cipher.decrypt(data)
        return data

    def send_encrypted_data(self, data, sock=None):
        sock = sock or self.sock
        data = self.cipher.encrypt(data)
        len_byte = len(data).to_bytes(2, "big")
        len_pad = random.randint(0, 255)
        len_data = (len_pad.to_bytes(1, "big") + len_byte + os.urandom(1)
                    if is_even(len_pad) else
                    len_byte + os.urandom(1) + len_pad.to_bytes(1, "big"))
        data = os.urandom(2) + len_data + data
        self.send_data(data, sock)


class LocalClimbServer(BaseClimbServer):
    """穿墙代理本地服务器"""

    def __init__(self, key, host="127.0.0.1", port=1080,
                 server_host='0.0.0.0', server_port=8324):
        super().__init__(key, host, port)
        self.server_host = server_host
        self.server_port = server_port

    def _connet_remote(self, addr, port, addr_data=None):
        remote = super()._connet_remote(self.server_host, self.server_port)
        self.send_encrypted_data(data=addr_data, sock=remote)
        data = self.recv_encrypted_data(sock=remote)
        affirm(data[0] == 0, "Remote server connection refused")
        return remote

    def _transfer_stream(self, sock, remote):
        """客户端和远程目的地址之间的数据流交换"""
        fdset = [sock, remote]
        while True:
            readset, writeset, exceptset = select.select(fdset, [], [])

            if sock in readset:
                data = self.recv_data(sock)
                if len(data) <= 0:
                    break
                self.send_encrypted_data(data, remote)

            if remote in readset:
                data = self.recv_encrypted_data(remote)
                if len(data) <= 0:
                    break
                self.send_data(data, sock)


class RemoteClimbServer(BaseClimbServer):
    """穿墙代理远程服务器"""

    def __init__(self, key, host="0.0.0.0", port=8324):
        super().__init__(key, host, port)

    def _check_auth(self, sock):
        pass

    def _handle_request(self, sock, addr):
        data = self.recv_encrypted_data(sock=sock)
        addr_type = data[0]
        if addr_type == 1:
            # IPv4 地址，目的地址为 4 字节长度
            remote_addr = socket.inet_ntoa(data[1:5])
        elif addr_type == 3:
            # 域名，第一个字节为域名长度，剩余的内容为域名
            addr_len = data[1]
            remote_addr = data[2:addr_len+2]
        elif addr_type == 4:
            # IPv6 地址，目的地址为 16 个字节长度
            remote_addr = socket.inet_ntop(socket.AF_INET6, data[1:17])
        else:
            # 不支持的地址类型
            reply = b'\x01' + os.urandom(random.randint(16, 32))
            self.send_encrypted_data(data=reply, sock=sock)
            raise Exception("Address type not supported: '%#x'" % addr_type)
        remote_addr = remote_addr.decode("utf-8")

        # 获取目的地址端口号，2 字节长度
        remote_port = struct.unpack('>H', data[-2:])[0]

        # 响应客户端的请求 SUCCESS
        reply = b'\x00' + os.urandom(random.randint(16, 32))
        self.send_encrypted_data(data=reply, sock=sock)

        # 尝试连接远程服务器，准备传输数据
        self.log.info("Connecting %s:%s from %s:%s",
                      remote_addr, remote_port, *addr)
        return self._connet_remote(remote_addr, remote_port)

    def _transfer_stream(self, sock, remote):
        """客户端和远程目的地址之间的数据流交换"""
        fdset = [sock, remote]
        while True:
            readset, writeset, exceptset = select.select(fdset, [], [])

            if sock in readset:
                data = self.recv_encrypted_data(sock)
                if len(data) <= 0:
                    break
                self.send_data(data, remote)

            if remote in readset:
                data = self.recv_data(remote)
                if len(data) <= 0:
                    break
                self.send_encrypted_data(data, sock)
