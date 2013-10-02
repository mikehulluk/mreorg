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
import re


class ScriptFlags(object):

    """Control the behaviour of matplotlib within scripts using environmental
    variables. This allows the script to act differently if its being used
    for interactive work or for producing the figures as part of a batch run.

    The environmental variables are read once during intiatisation. The
    behaviours can be changed during the script run by setting the relevant
    class attributes.
    """
    
    if not 'MREORG_CONFIG' in os.environ:
        raise RuntimeError(r'''
            The environmental variable "MREORG_CONFIG" is not set
            Perhaps you should set it, for example:
            export MREORG_CONFIG='SAVEALL;NOSHOW'
            or
            export MREORG_CONFIG=''
        ''')
    
    
    _expected_options_new = (
        'NOSHOW',
        'SAVEALL',
        'SAVEFIGADDINFO',
        'CURATIONRUN',
        'BATCHRUN',
        'ENABLECOVERAGE',
        'CURATION_REENTRYFLAG',
        'TIMEOUT',
        'MPLCONFIG',
        'NOMPLIMPORT',
        )

    mreorg_conf_string = os.environ['MREORG_CONFIG']
    mreorg_conf = re.split(r'[,;]', mreorg_conf_string)
    mreorg_conf = [m.strip() for m in mreorg_conf if m.strip()]

    for opt in mreorg_conf:
        if '=' in opt:
            continue
        assert opt in _expected_options_new, 'Unexpected option: %s' % opt

    ENVVAR_MREORG_NOSHOW = 'NOSHOW' in mreorg_conf
    ENVVAR_MREORG_NOMPLIMPORT = 'NOMPLIMPORT' in mreorg_conf
    ENVVAR_MREORG_SAVEALL = 'SAVEALL' in mreorg_conf
    ENVVAR_MREORG_SAVEFIGADDINFO = 'SAVEFIGADDINFO' in mreorg_conf
    ENVVAR_MREORG_CURATIONRUN = 'CURATIONRUN' in mreorg_conf
    ENVVAR_MREORG_BATCHRUN = 'BATCHRUN' in mreorg_conf
    ENVVAR_MREORG_ENABLECOVERAGE = 'ENABLECOVERAGE' in mreorg_conf
    ENVVAR_MREORG_CURATION_REENTRY = 'CURATION_REENTRYFLAG' in mreorg_conf

    # Temp Hack: lets turn coverage off!
    ENVVAR_MREORG_ENABLECOVERAGE = False

    # Don't call pylab.show() if ...
    MREORG_NOSHOW = ENVVAR_MREORG_NOSHOW or \
                    ENVVAR_MREORG_CURATIONRUN or \
                    ENVVAR_MREORG_BATCHRUN

    # Save all figures produced in the simulation:
    # This will happen when figures are produced and 'pylab.show()'
    # is called, or when the script ends.
    MREORG_SAVEALL = ENVVAR_MREORG_SAVEALL or \
                     ENVVAR_MREORG_CURATIONRUN or \
                     ENVVAR_MREORG_BATCHRUN

    # Copy, for the sake of interface consistency:
    MREORG_CURATIONRUN = ENVVAR_MREORG_CURATIONRUN

    MREORG_CURATION_REENTRY = ENVVAR_MREORG_CURATION_REENTRY

    # If we are building on read-the-docs, we can't import matplotlib:
    MREORG_DONTIMPORTMATPLOTLIB = 'READTHEDOCS' in os.environ or ENVVAR_MREORG_NOMPLIMPORT

    # Default, lets automatically create directories when they don't exist:
    MREORG_AUTOMAKEDIRS = True

    # Should we enable coverage:
    MREORG_ENABLECOVERAGE = ENVVAR_MREORG_ENABLECOVERAGE

    MREORG_SAVEFIGADDINFO = ENVVAR_MREORG_SAVEFIGADDINFO

    # Setup the environment:
    MREORG_MPLCONFIG = os.environ.get('MREORG_MPLCONFIG', None)
    
    MREORG_MPLCONFIG_FILE = None
    for opt in mreorg_conf:
        if opt.startswith('MPLCONFIG='):
            assert MREORG_MPLCONFIG_FILE == None
            mpl_conf_name = opt.split('=')[-1]
            currpath = os.path.dirname(os.path.abspath(__file__))
            mplconfigdir = os.path.join(currpath, '../../mplconfigs/')
            target_config_file = os.path.join(mplconfigdir,mpl_conf_name + '.conf')
            if not os.path.exists(target_config_file):
                assert False, "Can't find file: %s" % target_config_file
            MREORG_MPLCONFIG_FILE = target_config_file


    #if MREORG_MPLCONFIG:
    #    currpath = os.path.dirname( os.path.abspath(__file__) )
    #    mplconfigdir = os.path.join( currpath, '../../mplconfigs/')
    #    target_config_file = os.path.join(mplconfigdir,MREORG_MPLCONFIG + '.conf')
    #    if not os.path.exists(target_config_file):
    #        assert False, "Can't find file: %s" % target_config_file
    #    MREORG_MPLCONFIG_FILE=target_config_file
    #else:
    #    MREORG_MPLCONFIG_FILE=None

# Look out for unexpected flags:
for key in os.environ:
    if key.startswith('MREORG') and key != 'MREORG_CONFIG':
        if '=' in key:
            continue
        assert key in ScriptFlags._expected_options_new, 'MREORG config option not recognised: %s. Possible options: [%s]' % (key, ','.join(ScriptFlags._expected_options_new))
