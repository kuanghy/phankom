# -*- coding: utf-8 -*-

# *************************************************************
#  Copyright (c) Huoty - All rights reserved
#
#      Author: Huoty <sudohuoty@gmail.com>
#  CreateTime: 2017-11-11 15:05:48
# *************************************************************

import re
import ast
import types
import inspect
from collections import OrderedDict


def _make_assert_message(frame, regex):
    def extract_condition():
        code_context = inspect.getframeinfo(frame)[3]
        if not code_context:
            return ''
        match = re.search(regex, code_context[0])
        if not match:
            return ''
        return match.group(1).strip()

    class ReferenceFinder(ast.NodeVisitor):
        def __init__(self):
            self.names = []

        def find(self, tree, frame):
            self.visit(tree)
            nothing = object()
            deref = OrderedDict()
            for name in self.names:
                value = (frame.f_locals.get(name, nothing) or
                         frame.f_globals.get(name, nothing))
                _types = (types.ModuleType, types.FunctionType)
                if value is not nothing and not isinstance(value, _types):
                    deref[name] = repr(value)
            return deref

        def visit_Name(self, node):
            self.names.append(node.id)

    condition = extract_condition()
    if not condition:
        return
    deref = ReferenceFinder().find(ast.parse(condition), frame)
    deref_str = ''
    if deref:
        deref_str = ' with ' + ', '.join('{}={}'.format(k, v)
                                         for k, v in deref.items())
    return 'assertion {} failed{}'.format(condition, deref_str)


def affirm(condition, message=None):
    if condition:
        return

    if message:
        raise AssertionError(str(message))

    frame = inspect.currentframe().f_back
    regex = r'affirm\s*\(\s*(.+)\s*\)'
    message = _make_assert_message(frame, regex)

    raise AssertionError(message)


def is_even(x):
    return False if x & 1 else True
