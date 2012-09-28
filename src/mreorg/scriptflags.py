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


class ScriptFlags(object):

    """Control the behaviour of matplotlib within scripts using environmental
    variables. This allows the script to act differently if its being used
    for interactive work or for producing the figures as part of a batch run.

    The environmental variables are read once during intiatisation. The
    behaviours can be changed during the script run by setting the relevant
    class attributes.
    """

    osenv = os.environ
    ENVVAR_MREORG_NOSHOW = 'MREORG_NOSHOW' in osenv
    ENVVAR_MREORG_SAVEALL = 'MREORG_SAVEALL' in osenv
    ENVVAR_MREORG_SAVEFIGADDINFO = 'MREORG_SAVEFIGADDINFO' in osenv

    # 'Meta-options' that enable other options:
    ENVVAR_MREORG_CURATIONRUN = 'MREORG_CURATIONRUN' in osenv
    ENVVAR_MREORG_BATCHRUN = 'MREORG_BATCHRUN' in osenv

    ENVVAR_MREORG_ENABLECOVERAGE = 'MREORG_ENABLECOVERAGE' in osenv

    _expected_options = (
        'MREORG_NOSHOW',
        'MREORG_SAVEALL',
        'MREORG_SAVEFIGADDINFO',
        'MREORG_CURATIONRUN',
        'MREORG_BATCHRUN',
        'MREORG_ENABLECOVERAGE',
        'MREORG_CURATION_REENTRYFLAG',
        'MREORG_TIMEOUT',
        )

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

    # If we are building on read-the-docs, we can't import matplotlib:
    MREORG_DONTIMPORTMATPLOTLIB = 'READTHEDOCS' in os.environ

    # Default, lets automatically create directories when they don't exist:
    MREORG_AUTOMAKEDIRS = True

    # Should we enable coverage:
    MREORG_ENABLECOVERAGE = ENVVAR_MREORG_ENABLECOVERAGE

    MREORG_SAVEFIGADDINFO = ENVVAR_MREORG_SAVEFIGADDINFO


# Look out for unexpected flags:
for key in os.environ:
    if key.startswith('MREORG'):
        assert key in ScriptFlags._expected_options, 'MREORG config option not recognised: %s' % key
