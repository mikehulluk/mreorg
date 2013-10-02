#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import subprocess
import ast
import re
import sys


# A class that walks over python file contents, and extracts out
# string parameter calls to a function:
# ========================================

class MyFileWalker(ast.NodeVisitor):
    def __init__(self, funcname, argpos, *args, **kwargs):
        super(MyFileWalker, self).__init__(*args,**kwargs)
        self.calls = []
        self.argpos = argpos
        self.funcname = funcname

    def visit_Call(self, node):
        funcname = self.vis_attr(node.func)
        if funcname == self.funcname:
            arg = node.args[self.argpos]

            try:
                self.calls.append(arg.s)
            except:
                pass

    def vis_attr(self, n):
        if isinstance(n, basestring):
            return n
        elif isinstance(n, ast.Name):
            return self.vis_attr(n.id)
        elif isinstance(n, ast.Attribute):
            return self.vis_attr(n.attr)

        # Ignore more complex ast elements: indexing, subcalls
        elif isinstance(n, (ast.Subscript, ast.Call)):
            return None
        else:
            assert False, ' Unexpected node found %s' % type(n)

    @classmethod
    def get_all_func_calls(cls, src_contents, funcname, argpos=0):
        a = ast.parse(src_contents)
        x = cls(funcname=funcname, argpos=argpos)
        x.visit(a)
        return x.calls


# ========================================
