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
import fnmatch
import mreorg

import configobj
import validate
from os.path import expanduser


class MReOrgConfig(object):

    rcfilename = expanduser('~/.mreorgrc')
    localdir = os.path.join(os.path.dirname(__file__),'../..')
    configspecfilename = os.path.join(localdir, 'etc/configspec.ini')
    

    # New:
    # If the config file doesn't exist, make it from the defaults 
    # specified in the configspec.ini
    if not os.path.exists(rcfilename):
        config = configobj.ConfigObj(configspec=configspecfilename)
        validator = validate.Validator()
        config.validate(validator,copy=True)
        with open(rcfilename,'w') as f:
            config.write(f)
    config = configobj.ConfigObj(rcfilename, configspec=configspecfilename)
    validator = validate.Validator()
    config.validate(validator)
    
    
    
    @classmethod
    def get_image_store_dir(cls):
        path = cls.config['FileSystem']['Curate']['output_image_dir']
        return mreorg.utils.ensure_directory_exists(path)
        
    @classmethod
    def get_simulation_sqllite_filename(cls):
        path = cls.config['FileSystem']['Curate']['sqllite_filename']
        return mreorg.utils.ensure_directory_exists(path)


    @classmethod
    def is_non_curated_file(cls, filename):
        patterns = cls.config['Settings']['Curate']['filename_excludes']
        for pattern in patterns:
            if fnmatch.fnmatch(filename, pattern):
                return True
        return False

    
    
        
        
        
        #~ 
    #~ # Old:
    #~ _config_file_ns = None
#~ 
    #~ 
#~ 
    #~ _defaults = [
        #~ ('SIMULATION_SQLLITE_FILENAME', expanduser('~/.mreorg/mreorg.sqlite')),
        #~ ('SIMULATION_IMAGE_STOREDIR', expanduser('~/.mreorg/cache/images/')),
        #~ ('FILENAME_EXCLUDES', []), 
        #~ ('COVERAGE_OUTPUT_DIR', expanduser('~/.mreorg/coverage'))
    #~ ]
#~ 
    #~ 
#~ 
#~ 
    #~ @classmethod
    #~ def _load_config_file(cls):
#~ 
        #~ if cls._config_file_ns is not None:
            #~ return
        #~ assert False
        #~ # Start with a dictionary of defaults, then load in the rc-file
        #~ # file to override, if it exists:
        #~ cls._config_file_ns = dict(cls._defaults)
        #~ if os.path.exists(cls.rcfilename):
            #~ execfile(cls.rcfilename, cls._config_file_ns)
#~ 
    #~ @classmethod
    #~ def get_ns(cls):
        #~ cls._load_config_file()
        #~ return cls._config_file_ns
#~ 
    #~ @classmethod
    #~ def _get_path(cls, key, ensure_dir_exists=True):
        #~ path = cls.get_ns()[key]
        #~ if ensure_dir_exists:
            #~ mreorg.utils.ensure_directory_exists(path)
        #~ return path
#~ 
    #~ @classmethod
    #~ def get_image_store_dir(cls):
        #~ return cls._get_path('SIMULATION_IMAGE_STOREDIR')
#~ 
    #~ @classmethod
    #~ def get_simulation_sqllite_filename(cls):
        #~ return cls._get_path('SIMULATION_SQLLITE_FILENAME')
#~ 
#~ 
#~ 
#~ 
