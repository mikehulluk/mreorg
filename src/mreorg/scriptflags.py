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
import inspect, os


class ScriptFlags(object):

    """Control the behaviour of matplotlib within scripts using environmental
    variables. This allows the script to act differently if its being used
    for interactive work or for producing the figures as part of a batch run.

    The environmental variables are read once during intiatisation. The
    behaviours can be changed during the script run by setting the relevant
    class attributes.
    """

    # Allow mreorg.curate to run without needing to set flags:
    entry_point = inspect.stack()[-1][1]
    if 'mreorg.curate' in entry_point and not 'MREORG_CONFIG' in os.environ:
         os.environ['MREORG_CONFIG'] = ''


    if not 'MREORG_CONFIG' in os.environ and not 'mreorg.curate' in entry_point:
        raise RuntimeError(r'''
The environmental variable "MREORG_CONFIG" is not set
Perhaps you should set it, for example:
export MREORG_CONFIG='' # For no changes to Pylab behaviour
export MREORG_CONFIG='SAVEALL;NOSHOW' # To suppress 'show' and save figures instead
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

    # OK, lets look for a class named 'MReorgDefaults' in the calling function:
    import inspect
    top_caller = inspect.stack()[-1][0]
    mreorg_defaults = {}
    if 'MReorgDefaults' in top_caller.f_locals:
        for (k,v) in top_caller.f_locals['MReorgDefaults'].__dict__.items():
            if k in ('__doc__','__module__'):
                continue
            assert k in _expected_options_new
            mreorg_defaults[k] = v
            #print 'Using Default:', k, v


    

    # Vreak up the string into a dictionary, for things with an '='
    mreorg_conf_string = os.environ['MREORG_CONFIG']
    mreorg_conf = re.split(r'[,;]', mreorg_conf_string)
    mreorg_conf = [m.strip() for m in mreorg_conf if m.strip()]
    
    mreorg_conf = dict( [m.split("=") if '=' in m else (m,None) for m in mreorg_conf] )
    #print 'ConfigOoptins', mreorg_conf

    for opt in mreorg_conf:
        assert opt in _expected_options_new, 'Unexpected option: %s' % opt


    ENVVAR_MREORG_NOSHOW = ('NOSHOW' in mreorg_conf) or ('NOSHOW' in mreorg_defaults)
    ENVVAR_MREORG_NOMPLIMPORT = ('NOMPLIMPORT' in mreorg_conf) or ('NOMPLIMPORT' in mreorg_conf)
    ENVVAR_MREORG_SAVEALL = ('SAVEALL' in mreorg_conf) or ('SAVEALL' in mreorg_conf)
    ENVVAR_MREORG_SAVEFIGADDINFO = ('SAVEFIGADDINFO' in mreorg_conf) or ('SAVEFIGADDINFO' in mreorg_conf)
    ENVVAR_MREORG_CURATIONRUN = ('CURATIONRUN' in mreorg_conf) or ('CURATIONRUN' in mreorg_conf)
    ENVVAR_MREORG_BATCHRUN = ('BATCHRUN' in mreorg_conf) or ('BATCHRUN' in mreorg_conf)
    ENVVAR_MREORG_ENABLECOVERAGE = ('ENABLECOVERAGE' in mreorg_conf) or ('ENABLECOVERAGE' in mreorg_conf)
    ENVVAR_MREORG_CURATION_REENTRY = ('CURATION_REENTRYFLAG' in mreorg_conf) or ('CURATION_REENTRYFLAG' in mreorg_conf)
    


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
    MREORG_MPLCONFIG = None
    if 'MPLCONFIG' in mreorg_conf:
        MREORG_MPLCONFIG=mreorg_conf['MPLCONFIG']
    elif 'MPLCONFIG' in mreorg_defaults:
        MREORG_MPLCONFIG=mreorg_defaults['MPLCONFIG']

    MREORG_MPLCONFIG_FILE = None
    if MREORG_MPLCONFIG:
        currpath = os.path.dirname(os.path.abspath(__file__))
        mplconfigdir = os.path.join(currpath, '../../mplconfigs/')
        target_config_file = os.path.join(mplconfigdir,MREORG_MPLCONFIG + '.conf')
        if not os.path.exists(target_config_file):
            assert False, "Can't find file: %s" % target_config_file
        MREORG_MPLCONFIG_FILE = target_config_file
        print 'Using config file: ', target_config_file



# Look out for unexpected flags:
for key in os.environ:
    if key.startswith('MREORG') and key != 'MREORG_CONFIG':
        if '=' in key:
            continue
        assert key in ScriptFlags._expected_options_new, 'MREORG config option not recognised: %s. Possible options: [%s]' % (key, ','.join(ScriptFlags._expected_options_new))
