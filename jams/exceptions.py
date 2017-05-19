#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''Exception classes for JAMS'''


class JamsError(Exception):
    '''The root JAMS exception class'''
    pass


class SchemaError(JamsError):
    '''Exceptions relating to schema validation'''
    pass


class NamespaceError(JamsError):
    '''Exceptions relating to task namespaces'''
    pass


class ParameterError(JamsError):
    '''Exceptions relating to function and method parameters'''
    pass
