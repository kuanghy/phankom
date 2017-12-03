# -*- coding: utf-8 -*-

# *************************************************************
#  Copyright (c) Huoty - All rights reserved
#
#      Author: Huoty <sudohuoty@gmail.com>
#  CreateTime: 2017-10-28 16:53:07
# *************************************************************


from .log import setup_logging
from .socks import Socks5Server
from .break import LocalBreakServer


setup_logging()
# Socks5Server().start()
LocalBreakServer()
