#!/usr/bin/python
# -*- coding: utf-8 -*-

import re


class LyxFile(object):

    def __init__(self, filename):
        self.filename = filename

        with open(self.filename) as f:
            self.contents = f.read()

    def get_child_files(self):
        res = []
        im_re = re.compile(r'^\s*filename\s+(.*?)$', re.MULTILINE)
        for match in im_re.finditer(self.contents):
            dep_filename = match.groups()[0]
            res.append(dep_filename)

        return res


