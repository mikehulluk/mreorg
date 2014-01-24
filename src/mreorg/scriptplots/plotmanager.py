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
from mreorg.utils import ScriptUtils
from mreorg.layouts import FigureOptions
from mreorg.config import MReOrgConfig


class FigFormat:

    EPS = 'eps'
    SVG = 'svg'
    PDF = 'pdf'
    PNG = 'png'


class PlotManager:

    fig_num = 0
    figures_saved = []
    figures_saved_nums = []  # This is the numbers
    figures_saved_filenames = []

    _fig_loc = """_output/figures/{modulename}/{figtype}/"""
    _fig_name = """fig{fignum:03d}_{figname}.{figtype}"""
    autosave_default_image_filename_tmpl = _fig_loc + _fig_name

    autosave_image_formats = None
    _all_autosave_image_formats = [FigFormat.EPS, FigFormat.PDF,
                                   FigFormat.PNG, FigFormat.SVG]

    @classmethod
    def save_figure(
        cls,
        figname='',
        figure=None,
        filename_tmpl=None,
        figtypes=None,
        remap_dot_to_underscore=False,
        ):

        if remap_dot_to_underscore:
            figname = figname.replace('.', '-')

        if not filename_tmpl:
            filename_tmpl = cls.autosave_default_image_filename_tmpl
        if not figtypes:
            # Has it been set explicity in the class??
            if cls.autosave_image_formats is not None:
                figtypes = cls.autosave_image_formats

            # Is it specified in a layout config file:
            elif FigureOptions.default_autosave_formats is not None:
                figtypes = FigureOptions.default_autosave_formats
            # Or the rc file?
            elif 'Settings' in MReOrgConfig.config and \
                 'mreorg' in MReOrgConfig.config['Settings'] and \
                 'default_autosave_formats' in MReOrgConfig.config['Settings']['mreorg']:
                figtypes = MReOrgConfig.config['Settings']['mreorg']['default_autosave_formats']

            # No?, then lets default to everything:
            else:
                figtypes = cls._all_autosave_image_formats

        assert isinstance(figtypes, list), 'figtypes: %s <%s>'%(figtypes, type(figtypes))

        # Get the figure:
        import pylab
        fig = (figure if figure else pylab.gcf())

        # Some small changes:
        fig.subplots_adjust(bottom=0.15)

        # Find the module this function was called from:

        modname = ScriptUtils.get_calling_script_file(include_ext=False)

        # Print what we are saving:
        subst_dict = {
            'modulename': modname,
            'fignum': PlotManager.fig_num,
            'figname': figname,
            'figtype': '{%s}' % ','.join(figtypes),
            }
        print 'PlotManger saving: ', filename_tmpl.format(**subst_dict)

        # For each filetype:
        for figtype in figtypes:

            # Create the filename:
            subst_dict = {
                'modulename': modname,
                'fignum': PlotManager.fig_num,
                'figname': figname,
                'figtype': figtype,
                }

            filename = filename_tmpl.format(**subst_dict)
            filename = filename.replace(':', '=')
            assert not ':' in filename, 'For windows compatibility'

            # Save the figure:
            full_filename = os.path.join(os.getcwd(), filename)
            mreorg.ensure_directory_exists(full_filename)
            try:
                fig.savefig(full_filename)
            except ValueError as e:
                print 'mreorg error: unable to save figure: ', full_filename
                print e
                print '(ignoring error)'
            PlotManager.figures_saved.append(fig)
            PlotManager.figures_saved_nums.append(fig.number)
            PlotManager.figures_saved_filenames.append(full_filename)

        # Increment the fignum:
        PlotManager.fig_num = PlotManager.fig_num + 1

    @classmethod
    def save_active_figures(cls):
        import matplotlib

        active_figures = [manager.canvas.figure for manager in
                          matplotlib._pylab_helpers.Gcf.get_all_fig_managers()]
        active_figures_new = [a for a in active_figures if not a.number
                              in cls.figures_saved_nums]

        # Save the new figures:
        for fig in active_figures_new:
            if fig in PlotManager.figures_saved:
                continue

            PlotManager.save_figure(figname='Autosave_figure_%d'
                                    % fig.number, figure=fig)




