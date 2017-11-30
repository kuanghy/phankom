#! /usr/bin/env python
# -*- coding: utf-8 -*-

# *************************************************************
#  Copyright (c) Huoty - All rights reserved
#
#      Author: Huoty <sudohuoty@gmail.com>
#  CreateTime: 2017-10-28 16:56:59
# *************************************************************

"""加密混淆"""

import os
import zlib
import random
import hashlib
import itertools


def md5(data):
    m = hashlib.md5()
    m.update(data.encode("utf-8"))
    return m.hexdigest()


def sha1(data):
    return hashlib.sha1(data.encode("utf-8")).hexdigest()


class MixCipher(object):
    """混淆加密"""

    def __init__(self, key):
        self.salt = md5(key).encode("utf-8")

    def _xor_data(self, data):
        data = [(x ^ y).to_bytes(1, "big") for x, y in
                zip(data, itertools.cycle(self.salt))]
        return b"".join(data)

    def encrypt(self, data):
        data = self._xor_data(data)
        return zlib.compress(data)

    def decrypt(self, data):
        data = zlib.decompress(data)
        return self._xor_data(data)
