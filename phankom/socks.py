# -*- coding: utf-8 -*-

# *************************************************************
#  Copyright (c) Huoty - All rights reserved
#
#      Author: Huoty <sudohuoty@gmail.com>
#  CreateTime: 2017-10-28 16:41:09
# *************************************************************

"""Socks5 protocol frame"""

import re
import socket
import struct
import select
import logging
from threading import Thread

from .utils import affirm


class BaseSocks(object):
    """基础 Socks 协议"""

    BUFFER_SIZE = 10 * 1024

    AUTH_TYPES = {
        0x00: "NO_AUTH",
        0x01: "GSSAPI",
        0x02: "USERNAME_PASSWD",
        0xFF: "NO_SUPPORT_AUTH_METHOD"
    }

    REQUEST_COMMANDS = {
        0x01: "CONNECT",
        0x02: "BIND",
        0x03: "UDP_ASSOCIATE"
    }

    ADDR_TYPES = {
        0x01: "IPV4",
        0x03: "DOMAINNAME",
        0x04: "IPV6"
    }

    RESP_STATUS = {
        0x00: "SUCCESS",
        0x01: "GENRAL_FAILURE",
        0x02: "CONNECTION_NOT_ALLOWED",
        0x03: "NETWORK_UNREACHABLE",
        0x04: "HOST_UNREACHABLE",
        0x05: "CONNECTION_REFUSED",
        0x06: "TTL_EXPIRED",
        0x07: "COMMAND_NOT_SUPPORTED",
        0x08: "ADDRESS_TYPE_NOT_SUPPORTED"
    }

    def __init__(self):
        self.log = logging.getLogger()

        # 创建套接字
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 允许地址重用
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    @staticmethod
    def _check_protocol_version(version):
        affirm(version == 0x05, "Unsupported Protocol Version: '%s'" % version)

    def recv_data(self, sock=None, size=None):
        sock = sock or self.sock
        return sock.recv(size or self.BUFFER_SIZE)

    def send_data(self, data, sock=None):
        sock = sock or self.sock
        sock.sendall(data)

    @staticmethod
    def _get_addr_type(addr):
        if re.match(r'(\d{1,3}\.){3}\d{1,3}$', addr):
            return b'\x01'
        elif re.search(r'[a-zA-Z_]', addr):
            return b'\x02'
        else:
            return b'\x03'


class Socks5Server(BaseSocks):
    """Socks5 服务端

    特性:
        认证方式仅支持无需认证和用户名密码认证两种方式
        使用 IO 多路复用处理数据交换
        不支持 UDP 协议
    """

    def __init__(self, host='0.0.0.0', port=1080):
        self.host = host
        self.port = port

        super().__init__()

        self.sock.bind((self.host, self.port))
        self.sock.listen(5)

    def __user_auth(self, user, passwd):
        """用户名密码认证"""
        pass

    def _check_auth(self, sock):
        """校验认证方式"""
        data = sock.recv(256)

        version = data[0]
        self._check_protocol_version(version)

        methods_len = data[1]
        methods = [method for method in data[2:]]
        affirm(methods_len == len(methods),
               "NMETHODS Error: '%s != %s'" % (methods_len, len(methods)))

        method = methods[0]
        if method == 0x00:
            # 无需进一步认证
            sock.sendall(b"\x05\x00")
        elif method == 0x02:
            # 用户名密码认证方式
            sock.sendall(b"\x05\x02")
            self.__user_auth(sock)
        else:
            # 其他认证方式均不支持
            method = 0xFF
            sock.sendall(b"\x05\xFF")
            raise Exception(self.AUTH_TYPES[method])

    def _connet_remote(self, addr, port, addr_data=None):
        """连接远程服务器

        参数：
            addr: 远程服务器地址
            port: 远程服务器端口
            addr_data: 远程服务器地址信息，包括址类型(IPv4, IPv6, 域名)、地址内容部分
                该数据用于发给下一级中转服务器，由子类实现

        返回远程服务器连接套接字
        """
        return socket.create_connection((addr, port))

    def _handle_request(self, sock, addr):
        """处理请求信息"""
        data = sock.recv(4)
        affirm(data, "No request information")

        # 检查协议版本
        version = data[0]
        self._check_protocol_version(version)

        # 检查请求命令，只处理 CONNECT 请求
        cmd = data[1]
        affirm(cmd == 0x01, "Unsupported Request Command: '{}'".format(
                self.REQUEST_COMMANDS[cmd]))

        # 转换主机绑定的地址和端口为字节，响应客户端用
        host_addr = socket.inet_aton(self.host)
        host_port = struct.pack(">H", 8888)

        # 判断地址类型并获取目的地址
        addr_type = data[3]
        if addr_type == 1:
            # IPv4 地址，目的地址为 4 字节长度
            remote_addr_data = sock.recv(4)
            remote_addr = socket.inet_ntoa(remote_addr_data)
        elif addr_type == 3:
            # 域名，第一个字节为域名长度，剩余的内容为域名
            addr_len_data = sock.recv(1)
            addr_len = int.from_bytes(addr_len_data, byteorder='big')
            remote_addr = sock.recv(addr_len)
            remote_addr_data = addr_len_data + remote_addr
        elif addr_type == 4:
            # IPv6 地址，目的地址为 16 个字节长度
            remote_addr_data = sock.recv(16)
            remote_addr = socket.inet_ntop(socket.AF_INET6, remote_addr_data)
        else:
            # 不支持的地址类型
            reply = b"\x05\x08\x00\x00" + host_addr + host_port
            sock.send(reply)
            raise Exception("Address type not supported: '%#x'" % addr_type)
        remote_addr = remote_addr.decode("utf-8")

        # 获取目的地址端口号，2 字节长度
        remote_port_data = sock.recv(2)
        remote_port = struct.unpack('>H', remote_port_data)[0]

        # 响应客户端的请求 SUCCESS
        reply = b"\x05\x00\x00\x01" + host_addr + host_port
        sock.send(reply)

        # 尝试连接远程服务器，准备传输数据
        self.log.info("Connecting %s:%s from %s:%s",
                      remote_addr, remote_port, *addr)
        remote_addr_data = (struct.pack(">B", addr_type) +
                            remote_addr_data +
                            remote_port_data)
        return self._connet_remote(remote_addr, remote_port, remote_addr_data)

    def _transfer_stream(self, sock, remote):
        """客户端和远程目的地址之间的数据流交换"""
        fdset = [sock, remote]
        while True:
            readset, writeset, exceptset = select.select(fdset, [], [])

            if sock in readset:
                data = self.recv_data(sock)
                if len(data) <= 0:
                    break
                self.send_data(data, remote)

            if remote in readset:
                data = self.recv_data(remote)
                if len(data) <= 0:
                    break
                self.send_data(data, sock)

    def handle_connect(self, sock, addr):
        """处理连接请求"""
        remote = None  # 目的地址连接套接字
        try:
            self._check_auth(sock)
            remote = self._handle_request(sock, addr)
            self._transfer_stream(sock, remote)
        except Exception as e:
            self.log.warning(e)
        finally:
            if remote:
                remote.close()
            sock.close()

    def start(self):
        """启动服务器并等待连接，用线程处理每一个连接"""
        self.log.info("Starting at %s:%s", self.host, self.port)
        try:
            while True:
                sock, addr = self.sock.accept()
                thread = Thread(target=self.handle_connect, args=(sock, addr))
                thread.start()
        except Exception as e:
            self.log.error(e)


class Socks5Client(BaseSocks):
    """Socks5 客户端"""

    def __init__(self, proxy_host='0.0.0.0', proxy_port=1080,
                 user=None, passwd=None):
        super().__init__()

        self.user = user
        self.passwd = passwd

        self.sock.connet((proxy_host, proxy_port))

    def _handshake(self, addr):
        """与代理服务器握手"""
        # 协商版本和认证方法
        if self.user:
            pass
        else:
            self.send_data(b'\x05\x01\x00')

        data = self.recv_data(size=2)
        version = data[0]
        self._check_protocol_version(version)
        method = data[1]
        affirm(method == 0xFF, self.AUTH_TYPES[method])
        if method == 0x02:
            pass

        # 发送请求信息，暂不支持 IPv6 地址请求
        reply_data = b"\x05\x01\x00"
        if isinstance(addr, (tuple, list, set)):
            host_addr = addr[0]
            host_port = addr[1]
        else:
            host_addr = addr
            host_port = 80

        reply_data += self._get_addr_type(host_addr)

        host_addr = socket.inet_aton(host_addr)
        host_port = struct.pack(">H", host_addr)

        reply_data += host_addr + host_port

        self.send_data(reply_data)

    def connect(self, addr):
        """连接目的地址"""
        self._handshake(addr)
        self.send_data()
