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
import mreorg
# Lets monkey-patch matplotlib!
# ===============================

from mreorg.scriptflags import ScriptFlags
from mreorg.scriptplots import PlotManager
from mreorg.layouts import FigureOptions
from mreorg.utils import ScriptUtils


if not ScriptFlags.MREORG_DONTIMPORTMATPLOTLIB:

    import matplotlib

    # Preconfiguration, before we import pylab:
    if ScriptFlags.MREORG_MPLCONFIG_FILE:
        print 'Custom MPLConfig', ScriptFlags.MREORG_MPLCONFIG_FILE
        # Load the config file:
        from configobj import ConfigObj
        config = ConfigObj(ScriptFlags.MREORG_MPLCONFIG_FILE)


        # matplotlib config:
        mpl_rcparams = config.get('matplotlib',{})
        for (k,v) in mpl_rcparams.items():
            print "Setting: %s to %s" %(k,v)
            matplotlib.rcParams[k] = v


    # If we are running headless, then
    # explictly set the backend to something
    # that won't need $DISPLAY variable:
    if not os.environ.get('DISPLAY', None):
        matplotlib.use('Agg')




    # Monkey-Patch 'matplotlib.show()' and 'pylab.show()', allowing us
    # to disable them, and/or to save figures to disk.
    import pylab
    orig_mplshow = matplotlib.pylab.show


    def show(*args, **kwargs):
        # Should we save all the figures?
        if ScriptFlags.MREORG_SAVEALL:
            PlotManager.save_active_figures()

        # Should we actually display this:
        if ScriptFlags.MREORG_NOSHOW:
            pass
        else:
            orig_mplshow(*args, **kwargs)


    matplotlib.pylab.show = show
    pylab.show = show


    # Monkey-Patch 'matplotlib.savefig()' and 'pylab.savefig()', allowing us
    # to save to directories that don't exist by automatically creating them:
    orig_mplsavefig = matplotlib.pylab.savefig


    def savefig(filename, *args, **kwargs):
        if ScriptFlags.MREORG_SAVEFIGADDINFO or FigureOptions.is_draft:
            F = pylab.gcf()
            (x, y) = F.get_size_inches()
            txt = 'Size: x=%2.2f y=%2.2f (inches)' % (x, y)
            txt += '\n' + filename.split('/')[-1]
            txt += '\n' + ScriptUtils.get_calling_script_file(include_ext=True)
            pylab.figtext(0.0, 0.5, txt, backgroundcolor='white')


        if ScriptFlags.MREORG_AUTOMAKEDIRS:
            mreorg.ensure_directory_exists(filename)
        return orig_mplsavefig(filename, *args, **kwargs)

    matplotlib.pylab.savefig = savefig
    pylab.savefig = savefig

    # Monkey patch xlabel, ylabel, so the default is
    # multialignment='center'
    from matplotlib import axes
    set_xlabel_old = axes.Axes.set_xlabel
    set_ylabel_old = axes.Axes.set_ylabel
    
    def set_xlabel_new(self, *args, **kwargs):
        if not 'multialignment' in kwargs:
            kwargs['multialignment'] = 'center'
        return set_xlabel_old(self, *args, **kwargs)
    def set_ylabel_new(self, *args, **kwargs):
        if not 'multialignment' in kwargs:
            kwargs['multialignment'] = 'center'
        return set_ylabel_old(self, *args, **kwargs)
    axes.Axes.set_xlabel = set_xlabel_new
    axes.Axes.set_ylabel = set_ylabel_new




# Hook in the coverage
if ScriptFlags.MREORG_ENABLECOVERAGE:
    import mreorg.config
    conf = mreorg.config.MReOrgConfig.get_ns()
    coverage_opdir = conf['COVERAGE_OUTPUT_DIR']
    if not os.path.exists(coverage_opdir):
        os.makedirs(coverage_opdir)
    os.environ['COVERAGE_PROCESS_START'] = conf['COVERAGE_CONFIG_FILE']
    import coverage
    coverage.process_startup()

if ScriptFlags.MREORG_CURATIONRUN:
    from mreorg.curator.backend_sim.db_writer_hooks import CurationSimDecorator
    CurationSimDecorator.activate()





