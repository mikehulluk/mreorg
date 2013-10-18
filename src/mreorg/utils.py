#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
# Copyright (c) 2012 Michael Hull.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  - Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  - Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY
# WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------

import inspect
import os

import hashlib
import tokenize
import token
import contextlib


class ScriptUtils(object):

    @classmethod
    def get_calling_script(cls):
        frame = inspect.stack()

        callee_frame = frame[-1]
        callee_file = callee_frame[1]
        return callee_file

    @classmethod
    def get_calling_script_directory(cls):
        return os.path.dirname(cls.get_calling_script())

    @classmethod
    def get_calling_script_file(cls, include_ext):
        filename = os.path.basename(cls.get_calling_script())
        if include_ext:
            return filename
        else:
            return os.path.splitext(filename)[0]


def extract_docstring_from_fileobj(fileobj):
    for token_data in tokenize.generate_tokens(fileobj.readline):
        tok = token_data[0]
        text = token_data[1]
        if tok in [tokenize.COMMENT, tokenize.NL]:
            continue
        elif tok in [tokenize.NAME, tokenize.ENDMARKER]:
            return None
        elif tok == tokenize.STRING:
            text = text.strip()
            if text.startswith('"""'):
                text = text[3:]
            if text.endswith('"""'):
                text = text[:-3]
            return text.strip()
        else:
            tokenname = token.tok_name[tok]
            msg = 'Unexpected token %s (%s)' % (tokenname, tok)
            raise ValueError(msg)
    return None


def ensure_directory_exists(filename, is_dir=False):
    dirname = os.path.dirname(filename) if not is_dir else filename
    if not os.path.exists(dirname) and dirname.strip():
        os.makedirs(dirname)
    return filename


def get_file_sha1hash(filename):
    hash_obj = hashlib.sha1()
    with open(filename) as fileobj:
        hash_obj.update(fileobj.read())
    return hash_obj.hexdigest()


@contextlib.contextmanager
def switch_into_working_directory(path):
    """A context manager which changes the working directory to the given
    path, and then changes it back to its previous value on exit.
    """
    prev_cwd = os.getcwd()
    os.chdir(path)
    try:
        yield None
    finally:
        os.chdir(prev_cwd)

