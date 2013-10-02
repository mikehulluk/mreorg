#!/usr/bin/python
# -*- coding: utf-8 -*-

from pyfile_astwalker import MyFileWalker
import re


class PyFile(object):

    def __init__(self, filename):
        self.filename = filename
        assert filename.endswith('.py')

        with open(self.filename) as f:
            self.contents = f.read()

    def get_cleaned_version(self):
        txt = self.contents
        toggle_block = '##==TOGGLE=='
        if toggle_block in txt:
            blocks = txt.split(toggle_block)
            txt = ''.join(blocks[1::2])

        txt = txt.strip()
        return txt


class PyFileScons(PyFile):
    def __init__(self, filename):
        super(PyFileScons,self).__init__(filename=filename)
        
        
        
    def get_output_files(self):
        includes_1 = MyFileWalker.get_all_func_calls(self.contents, 'savefig', argpos=0)
        includes_2 = MyFileWalker.get_all_func_calls(self.contents, 'save', argpos=0)

        # OUTPUT: 'filename' lines
        includes_3 = []
        re_outputline = re.compile(r"""#\s*OUTPUT:\s*'(.*)'\s*$""", re.MULTILINE)
        for match in re_outputline.finditer(self.contents):
            includes_3.append(match.groups()[0])

        includes = includes_1 + includes_2 + includes_3

        return includes

    def get_dependancy_files(self):

        includes1a = MyFileWalker.get_all_func_calls(self.contents, 'add_file', argpos=1)
        includes1b = MyFileWalker.get_all_func_calls(self.contents, 'add_file_mpl', argpos=1)
        includes = includes1a + includes1b

        includes2 = []
        re_outputline = re.compile(r"""#\s*INPUT:\s*'(.*)'\s*$""", re.MULTILINE)
        for match in re_outputline.finditer(self.contents):
            includes2.append(match.groups()[0])

        return includes + includes2

