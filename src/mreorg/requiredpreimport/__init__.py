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

from mreorg.scriptflags import ScriptFlags
from mreorg.layouts import FigureOptions
import datetime

# Lets monkey-patch matplotlib!
# ===============================

if not ScriptFlags.MREORG_DONTIMPORTMATPLOTLIB:
    import matplotlib
    is_running_headless = not os.environ.get('DISPLAY', None)


    # Preconfiguration, before we import pylab:
    if ScriptFlags.MREORG_MPLCONFIG_FILE:
        print 'Custom MPLConfig', ScriptFlags.MREORG_MPLCONFIG_FILE
        # Load the config file:
        from configobj import ConfigObj
        config = ConfigObj(ScriptFlags.MREORG_MPLCONFIG_FILE)

        # Setup the backend:
        backend = None
        if is_running_headless:
            if 'mpl_backend_headless' in config['options']:
                backend = config['options']['mpl_backend_headless']
            else:
                backend = config['options']['mpl_backend']
        else:
            backend = config['options']['mpl_backend']

        assert backend, 'No backend set for config: %s' % ScriptFlags.MREORG_MPLCONFIG_FILE
        matplotlib.use(backend)

        # Setup the rc-params values:
        mpl_rcparams = config.get('matplotlib', {})

        # Downscale values set in mreorg, if needs be. (This is to work around a bug(?) in matplotlib SVG backend):
        downscale_options = ['font.size','axes.labelsize','legend.fontsize','xtick.labelsize','ytick.labelsize']
        if FigureOptions.downscale_fontsize:
            for k in downscale_options:
                if k in mpl_rcparams.keys():
                    mpl_rcparams[k] = float(mpl_rcparams[k]) / FigureOptions.downscale_fontsize

        for (k, v) in mpl_rcparams.items():
            print 'Setting: %s to %s' % (k, v)
            matplotlib.rcParams[k] = v

    # Monkey-Patch 'matplotlib.show()' and 'pylab.show()', allowing us
    # to disable them, and/or to save figures to disk.
    import pylab
    orig_mplshow = matplotlib.pylab.show


    def show(*args, **kwargs):
        from mreorg.scriptplots import PlotManager
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
        from mreorg.layouts import FigureOptions
        from mreorg.utils import ScriptUtils
        if ScriptFlags.MREORG_SAVEFIGADDINFO or FigureOptions.is_draft:
            F = pylab.gcf()
            (x, y) = F.get_size_inches()
            txt = 'Size: x=%2.2f y=%2.2f (inches)' % (x, y)
            txt += '\n' + 'On: %s' % datetime.datetime.today().strftime('%d, %h %Y (%H:%M)')
            txt += '\n' + 'Using MPLCONFIGFILE: %s' % ScriptFlags.MREORG_MPLCONFIG_FILE
            txt += '\n' + filename.split('/')[-1]
            txt += '\n' + ScriptUtils.get_calling_script_file(include_ext=True)
            pylab.figtext(0.0, 0.5, txt, backgroundcolor='white')

        if ScriptFlags.MREORG_AUTOMAKEDIRS:
            mreorg.ensure_directory_exists(filename)
        return orig_mplsavefig(filename, *args, transparent=True, **kwargs)

    matplotlib.pylab.savefig = savefig
    pylab.savefig = savefig





    ## Trigger saving all images at the end of the program run:
    #if ScriptFlags.MREORG_SAVEALL:
    #    
    #    from mreorg.atexithandlers import AtExitHandler
    #    def _save_all_at_exit(*args,**kwargs):
    #        print 'Saving atexit:'
    #        from mreorg.scriptplots import PlotManager
    #        PlotManager.save_active_figures()


    #    AtExitHandler.add_handler(_save_all_at_exit)









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

    hack_options = mreorg.MReOrgConfig.config['Settings']['mreorg']['Hacks']
    if hack_options['xlabel_multialign_centre']:
        axes.Axes.set_xlabel = set_xlabel_new
    if hack_options['ylabel_multialign_centre']:
        axes.Axes.set_ylabel = set_ylabel_new


    # SVG hack
    # SVG output is a problem, because of a conversion between pt to px, which I don't really understand.
    # we interecept the call to 'draw_text' at a really low level, in order to rescale the font:
    do_hack=hack_options['svg_downscale'] 
    do_hack=True
    if matplotlib.get_backend() == 'svg' and FigureOptions.downscale_fontsize_hack and do_hack:
        import matplotlib.backends.backend_svg as svg
        def myfunc(self, ctx, x, y,  text, fp, *args,**kwargs):
            fp = fp.copy()
            fp.set_size(fp.get_size() / 1.25) 
            orig = getattr(self, 'mreorg_draw_text')
            return orig( ctx,x,y, text, fp,*args, **kwargs)
        # Rename the original method
        setattr( svg.RendererSVG, 'mreorg_draw_text', getattr(svg.RendererSVG,'draw_text') )
        setattr( svg.RendererSVG, 'draw_text', myfunc)


# Hook in the coverage
if ScriptFlags.MREORG_ENABLECOVERAGE:
    import mreorg.config
    print 'Activating Coverage'
    coverage_opdir = mreorg.config.MReOrgConfig.get_coverage_store_dir()
    os.environ['COVERAGE_PROCESS_START'] = mreorg.config.MReOrgConfig.get_coverage_configfile()

    import coverage
    coverage.process_startup()



if ScriptFlags.MREORG_CURATIONRUN:
    #assert False
    from mreorg.curator.backend_sim.db_writer_hooks import CurationSimDecorator
    CurationSimDecorator.activate()

