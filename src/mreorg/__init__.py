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

import os
import sys

# Ensure our monkey patching takes place first:
import mreorg.requiredpreimport

from mreorg.scriptplots import PlotManager, PM
from mreorg.scriptplots import FigFormat
from mreorg.scriptflags import ScriptFlags
from mreorg.utils import ensure_directory_exists
from mreorg.config import MReOrgConfig

from mreorg.utils import get_file_sha1hash

from mreorg.layouts import FigureLayouts
from mreorg.layouts import FigureOptions


# Setup glob2 path
# ----------------
local_dir = os.path.dirname(__file__)
glob2_src_dir = os.path.join(local_dir,'../../dependances/glob2/src/')
sys.path.append(glob2_src_dir)
import glob2

__all__ = [
    'MReOrgConfig',
    'ScriptFlags',
    'PlotManager',
    'PM',
    'FigFormat',
    'ensure_directory_exists',
    'get_file_sha1hash',
    'glob2',
    'FigureLayouts',
    'FigureOptions',
    
]
