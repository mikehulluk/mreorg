#!/usr/bin/python
# -*- coding: utf-8 -*-
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
import re


class ScriptFlags(object):
    """Control the behaviour of matplotlib within scripts using environmental
    variables. This allows the script to act differently if its being used
    for interactive work or for producing the figures as part of a batch run.

    The environmental variables are read once during intiatisation. The
    behaviours can be changed during the script run by setting the relevant
    class attributes.
    """

    _expected_options = (
        'MREORG_NOSHOW',
        'MREORG_SAVEALL',
        'MREORG_SAVEFIGADDINFO',
        'MREORG_CURATIONRUN',
        'MREORG_BATCHRUN',
        'MREORG_ENABLECOVERAGE',
        'MREORG_CURATION_REENTRYFLAG',
        'MREORG_TIMEOUT',
        'MREORG_MPLCONFIG',
        'MREORG_NOMPLIMPORT',
        )

    # Old Style - using individual config variables [to remove]
    osenv = os.environ
    old_ENVVAR_MREORG_NOSHOW = 'MREORG_NOSHOW' in osenv
    old_ENVVAR_MREORG_NOMPLIMPORT = 'MREORG_NOMPLIMPORT' in osenv
    old_ENVVAR_MREORG_SAVEALL = 'MREORG_SAVEALL' in osenv
    old_ENVVAR_MREORG_SAVEFIGADDINFO = 'MREORG_SAVEFIGADDINFO' in osenv
    # 'Meta-options' that enable other options:
    old_ENVVAR_MREORG_CURATIONRUN = 'MREORG_CURATIONRUN' in osenv
    old_ENVVAR_MREORG_BATCHRUN = 'MREORG_BATCHRUN' in osenv
    old_ENVVAR_MREORG_ENABLECOVERAGE = 'MREORG_ENABLECOVERAGE' in osenv


    # New Style:
    mreorg_conf_string = os.environ['MREORG_CONFIG']
    mreorg_conf = re.split(r'\W+', mreorg_conf_string)
    _expected_options_new = [exp_opt.replace("MREORG_","") for exp_opt in _expected_options]
    for opt in mreorg_conf:
        assert opt in _expected_options_new, 'Unexpected option: %s' % opt
    new_ENVVAR_MREORG_NOSHOW = 'NOSHOW' in mreorg_conf
    new_ENVVAR_MREORG_NOMPLIMPORT = 'NOMPLIMPORT' in mreorg_conf
    new_ENVVAR_MREORG_SAVEALL = 'SAVEALL' in mreorg_conf
    new_ENVVAR_MREORG_SAVEFIGADDINFO = 'SAVEFIGADDINFO' in mreorg_conf
    new_ENVVAR_MREORG_CURATIONRUN = 'CURATIONRUN' in mreorg_conf
    new_ENVVAR_MREORG_BATCHRUN = 'BATCHRUN' in mreorg_conf
    new_ENVVAR_MREORG_ENABLECOVERAGE = 'ENABLECOVERAGE' in mreorg_conf


    # Allow either old or new for the time being:
    ENVVAR_MREORG_NOSHOW = old_ENVVAR_MREORG_NOSHOW or new_ENVVAR_MREORG_NOSHOW
    ENVVAR_MREORG_NOMPLIMPORT = old_ENVVAR_MREORG_NOMPLIMPORT or new_ENVVAR_MREORG_NOMPLIMPORT
    ENVVAR_MREORG_SAVEALL = old_ENVVAR_MREORG_SAVEALL or new_ENVVAR_MREORG_SAVEALL
    ENVVAR_MREORG_SAVEFIGADDINFO = old_ENVVAR_MREORG_SAVEFIGADDINFO or new_ENVVAR_MREORG_SAVEFIGADDINFO
    ENVVAR_MREORG_CURATIONRUN = old_ENVVAR_MREORG_CURATIONRUN or new_ENVVAR_MREORG_CURATIONRUN
    ENVVAR_MREORG_BATCHRUN = old_ENVVAR_MREORG_BATCHRUN or new_ENVVAR_MREORG_BATCHRUN
    ENVVAR_MREORG_ENABLECOVERAGE = old_ENVVAR_MREORG_ENABLECOVERAGE or new_ENVVAR_MREORG_ENABLECOVERAGE





    # Temp Hack: lets turn coverage off!
    ENVVAR_MREORG_ENABLECOVERAGE =  False

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

    # If we are building on read-the-docs, we can't import matplotlib:
    MREORG_DONTIMPORTMATPLOTLIB =  'READTHEDOCS' in os.environ or ENVVAR_MREORG_NOMPLIMPORT

    # Default, lets automatically create directories when they don't exist:
    MREORG_AUTOMAKEDIRS = True

    # Should we enable coverage:
    MREORG_ENABLECOVERAGE = ENVVAR_MREORG_ENABLECOVERAGE

    MREORG_SAVEFIGADDINFO =  ENVVAR_MREORG_SAVEFIGADDINFO


    # Setup the environment:
    MREORG_MPLCONFIG =  osenv.get('MREORG_MPLCONFIG', None)
    if MREORG_MPLCONFIG:
        currpath = os.path.dirname( os.path.abspath(__file__) )
        mplconfigdir = os.path.join( currpath, '../../mplconfigs/')
        target_config_file = os.path.join(mplconfigdir,MREORG_MPLCONFIG + '.conf')
        if not os.path.exists(target_config_file):
            assert False, "Can't find file: %s" % target_config_file
        MREORG_MPLCONFIG_FILE=target_config_file
    else:
        MREORG_MPLCONFIG_FILE=None





# Look out for unexpected flags:
for key in os.environ:
    if key.startswith('MREORG') and key != 'MREORG_CONFIG':
        assert key in ScriptFlags._expected_options, 'MREORG config option not recognised: %s. Possible options: [%s]' % (key, ','.join(ScriptFlags._expected_options))
