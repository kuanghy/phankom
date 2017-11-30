# -*- coding: utf-8 -*-

# *************************************************************
#  Copyright (c) JoinQuant Development Team
#
#  Author: Huayong Kuang <kuanghuayong@joinquant.com>
#  CreateTime: 2017-06-19 09:43:16 Monday
# *************************************************************

"""日志模块"""

import sys
import logging


class ColoredStreamHandler(logging.StreamHandler):
    """带色彩的流日志处理器"""

    C_BLACK = '\033[0;30m'
    C_RED = '\033[0;31m'
    C_GREEN = '\033[0;32m'
    C_BROWN = '\033[0;33m'
    C_BLUE = '\033[0;34m'
    C_PURPLE = '\033[0;35m'
    C_CYAN = '\033[0;36m'
    C_GREY = '\033[0;37m'

    C_DARK_GREY = '\033[1;30m'
    C_LIGHT_RED = '\033[1;31m'
    C_LIGHT_GREEN = '\033[1;32m'
    C_YELLOW = '\033[1;33m'
    C_LIGHT_BLUE = '\033[1;34m'
    C_LIGHT_PURPLE = '\033[1;35m'
    C_LIGHT_CYAN = '\033[1;36m'
    C_WHITE = '\033[1;37m'

    C_RESET = "\033[0m"

    def __init__(self, *args, **kwargs):
        self._colors = {logging.DEBUG: self.C_DARK_GREY,
                        logging.INFO: self.C_RESET,
                        logging.WARNING: self.C_BROWN,
                        logging.ERROR: self.C_RED,
                        logging.CRITICAL: self.C_LIGHT_RED}
        super(ColoredStreamHandler, self).__init__(*args, **kwargs)

    @property
    def is_tty(self):
        isatty = getattr(self.stream, 'isatty', None)
        return isatty and isatty()

    def emit(self, record):
        try:
            message = self.format(record)
            stream = self.stream
            if not self.is_tty:
                stream.write(message)
            else:
                message = self._colors[record.levelno] + message + self.C_RESET
                stream.write(message)
            stream.write(getattr(self, 'terminator', '\n'))
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.handleError(record)

    def setLevelColor(self, logging_level, escaped_ansi_code):
        self._colors[logging_level] = escaped_ansi_code


DEFAULT_LOG_FORMAT = "[%(levelname)1.1s %(asctime)s] %(message)s"


def setup_logging(reset=False):
    logger = logging.getLogger()

    if len(logger.handlers) > 0 and not reset:
        logger.debug("logging has been set up")
        return

    # empty handlers
    logger.handlers = []

    logger.setLevel(logging.DEBUG)

    # add stream log handler for info
    stream_handler = ColoredStreamHandler(sys.stdout)
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))
    logger.addHandler(stream_handler)
