#----------------------------------------------------------------------
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
#----------------------------------------------------------------------

import os
import mreorg

class MReOrgConfig(object):
    _config_file_ns = None

    rcfilename = os.path.expanduser('~/.mreorgrc')

    _defaults = [
        ('IMAGE_STORE_DIR', os.path.expanduser('~/.mreorg/cache/images/'))
        ]

    @classmethod
    def _load_config_file(cls):
        if cls._config_file_ns is None:
            
            # Copy in the defaults:
            cls._config_file_ns = dict( cls._defaults)
            
            # Load the file, overriding the defaults:
            if not os.path.exists( cls.rcfilename ):
                return
            execfile(cls.rcfilename, cls._config_file_ns)
            
    @classmethod
    def get_ns(cls):
        cls._load_config_file()
        return cls._config_file_ns


    @classmethod
    def get_image_store_dir(cls):
        return mreorg.ensure_directory_exists( cls.get_ns()['IMAGE_STORE_DIR'] )
