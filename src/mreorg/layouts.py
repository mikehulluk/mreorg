#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

from mreorg.scriptflags import ScriptFlags

try:
    from validate import Validator
except ImportError:
    print "Unable to import 'Validator'"


class _FigureLayouts(object):

    def __init__(self):

        # Load the config file:
        if ScriptFlags.MREORG_MPLCONFIG_FILE:
            from configobj import ConfigObj
            config = ConfigObj(ScriptFlags.MREORG_MPLCONFIG_FILE,interpolation='template')
            config.interpolation = 'template'

            for k in config.get('layouts', {}):
                self.__dict__[str(k)] = config['layouts'][k]

    def get_xy_in(self, xname, yname):
        print self.__dict__
        x = float(self.__dict__[xname]) / 25.4
        y = float(self.__dict__[yname]) / 25.4
        return (x, y)






class _FigureOptions(object):

    _defaults = {
            'draft':False,
            'default_autosave_formats' : None,
            'downscale_fontsize_hack' :False,
            }

    
    local_dir = os.path.dirname(__file__)
    _configspecfile = os.path.join(local_dir, '../../mplconfigs/mplconfig.spec')

    def __init__(self):
        self.default_autosave_formats = None
        # Load the defaults:
        self.__dict__.update(_FigureOptions._defaults)

        # Load the config file:
        if ScriptFlags.MREORG_MPLCONFIG_FILE:
            from configobj import ConfigObj

            config = ConfigObj(ScriptFlags.MREORG_MPLCONFIG_FILE, interpolation='template', configspec=_FigureOptions._configspecfile)
            validator = Validator()
            result = config.validate(validator)
            assert result == True, 'Invalid Config for mreorg'

            self.__dict__.update(config.get('options',{}))


    @property
    def is_draft(self):
        return self.draft


FigureLayouts = _FigureLayouts()
FigureOptions = _FigureOptions()

