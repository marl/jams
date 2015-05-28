#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''Exception classes for JAMS'''

class JamsError(Exception):
    '''The root JAMS exception class'''
    pass


class ValidationError(JamsError):
    '''Exceptions relating to schema validation'''


class NamespaceError(JamsError):
    '''Exceptions relating to task namespaces'''


class ParameterError(JamsError):
    '''Exceptions relating to function and method parameters'''

class MatchError(JamsError):
    '''Exceptions relating to alignment'''
