#! /usr/bin/env python
# -*- coding: utf-8 -*-

# *************************************************************
#  Copyright (c) Huoty - All rights reserved
#
#      Author: Huoty <sudohuoty@gmail.com>
#  CreateTime: 2017-11-19 19:16:34
# *************************************************************

import os
import random

from phankom.crypt import MixCipher


class TestMixCipher(object):

    def setup_class(self):
        self.cipher = MixCipher("hello")

    def teardown_class(self):
        pass

    def test_xor_data(self):
        assert self.cipher.salt == b'5d41402abc4b2a76b9719d911017c592'
        self.cipher._xor_data(b'\x00\x01\x06\x09') == b'5e28'

    def test_encrypt(self):
        data = os.urandom(random.randint(1, 256))
        encrypted_data = self.cipher.encrypt(data)
        assert self.cipher.decrypt(encrypted_data) == data

    def test_decrypt(self):
        data = b'x\x9c\xbb\x1e\xc3Q\xa8\xf4u\xf6\xdb\xa3f\x7fX\xc2\xd8Y\x19\xd9\x00IY\x06\xb0'
        assert self.cipher.decrypt(data) == b'123456'
