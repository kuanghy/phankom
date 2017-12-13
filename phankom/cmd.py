#! /usr/bin/env python
# -*- coding: utf-8 -*-

# *************************************************************
#  Copyright (c) Huoty - All rights reserved
#
#      Author: Huoty <sudohuoty@gmail.com>
#  CreateTime: 2017-12-09 22:40:44
# *************************************************************

from __future__ import print_function

import logging
from argparse import ArgumentParser

from .__init__ import __version__ as version
from .log import setup_logging


def create_argument(parser, *args, **kwargs):
    parser.add_argument(*args, **kwargs)


def parse_arguments():
    parser = ArgumentParser(description="Phankom is a proxy tool",
                            epilog="Use 'phankom COMMAND --help' for more "
                                   "information on a command.")
    create_argument(parser, "-v", "--version", action='version', version=version)
    subparsers = parser.add_subparsers(title='Commands', dest="subparser")

    parser_socks = subparsers.add_parser("socks", help="Scoks proxy")
    create_argument(parser_socks, "--loglevel", default="info",
                    choices=["debug", "info", "warning", "error", "fatal", "critical"],
                    help="Log level (default: info)")
    create_argument(parser_socks, "-H", "--host", default="0.0.0.0",
                    help="hostname to listen on (default: 0.0.0.0)")
    create_argument(parser_socks, "-p", "--port", default=1080,
                    help="port of the server (default: 1080)")

    parser_climb = subparsers.add_parser("climb", help="Climb over the GFW")
    create_argument(parser_climb, "--loglevel", default="info",
                    choices=["debug", "info", "warning", "error", "fatal", "critical"],
                    help="Log level (default: info")
    create_argument(parser_climb, "-c", "--client", action="store_true",
                    help="Client mode")
    create_argument(parser_climb, "-s", "--server", action="store_true",
                    help="Server mode")
    create_argument(parser_climb, "-k", "--key", default="qwer1234",
                    help="Secret key string (default: qwer1234)")
    create_argument(parser_climb, "-H", "--host",
                    help="Hostname to listen on"
                         "(clinet default: 127.0.0.1, server default: 0.0.0.0)")
    create_argument(parser_climb, "-p", "--port",
                    help="Port of the server"
                         "(clinet default: 1080, server default: 8324)")

    parser_climb_client_group = parser_climb.add_argument_group('client arguments')
    create_argument(parser_climb_client_group, "--server-host", default="127.0.0.1",
                    help="Remote server hostname (default: 127.0.0.1)")
    create_argument(parser_climb_client_group, "--server-port", default=8324,
                    help="Remote server port (default: 8324)")

    parser_http = subparsers.add_parser("http", help="Climb over the GFW")
    create_argument(parser_http, "--loglevel", default="info",
                    choices=["debug", "info", "warning", "error", "fatal", "critical"],
                    help="Log level (default: info")

    return parser.parse_args()


def main():
    args = parse_arguments()

    setup_logging()
    logging.getLogger().setLevel(getattr(logging, args.loglevel.upper()))

    if args.subparser == "socks":
        from .socks import Socks5Server
        ss = Socks5Server(args.host, args.port)
        ss.start()
    elif args.subparser == "climb":
        from .climb import LocalClimbServer, RemoteClimbServer
        if args.server:
            args.host = args.host or "0.0.0.0"
            args.port = args.port or 8324
            rcs = RemoteClimbServer(args.key, args.host, args.port)
            rcs.start()
        else:
            args.host = args.host or "127.0.0.1"
            args.port = args.port or 1080
            lcs = LocalClimbServer(args.key, args.host, args.port,
                                   args.server_host, args.server_port)
            lcs.start()
    else:
        print("Invalid command, see 'jqarena --help'")
