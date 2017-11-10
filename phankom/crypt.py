#! /usr/bin/env python
# -*- coding: utf-8 -*-

# *************************************************************
#  Copyright (c) Huoty - All rights reserved
#
#      Author: Huoty <sudohuoty@gmail.com>
#  CreateTime: 2017-10-28 16:56:59
# *************************************************************

"""加密混淆"""


import hashlib
import itertools


def md5(data):
    m = hashlib.md5()
    m.update(data.encode("utf-8"))
    return m.hexdigest()


def sha1(data):
    return hashlib.sha1(data.encode("utf-8")).hexdigest()


class Mixer(object):
    """数据混淆器"""

    def __init__(self, key=None):
        self.salt = md5(key).encode("utf-8")

    def _xor_data(self, data):
        return "".join([x ^ y for x, y in zip(data, itertools.cycle(self.salt))])

    @staticmethod
    def _to_bytes(data):
        return data if isinstance(data, bytes) else data.encode("utf-8")

    def encrypt(self, data):
        return self._xor_data(self._to_bytes(data))

    def decrypt(self, data):
        return self._xor_data(self._to_bytes(data))
