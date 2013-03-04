

from mreorg.scriptflags import ScriptFlags


class _FigureLayouts():

    def __init__(self,):

        # Load the config file:
        if ScriptFlags.MREORG_MPLCONFIG_FILE:
            from configobj import ConfigObj
            config = ConfigObj(ScriptFlags.MREORG_MPLCONFIG_FILE,interpolation='template')
            config.interpolation = 'template'

            for k in config.get('layouts',{}):
                self.__dict__[str(k)] = config['layouts'][k]


    def get_xy_in(self, xname,yname):
        print self.__dict__
        x = float(self.__dict__[xname]) / 25.4
        y = float(self.__dict__[yname]) / 25.4
        return (x,y)






class _FigureOptions():

    _defaults = {
            'draft':False,
            'default_autosave_formats' : None
            }

    def __init__(self,):
        self.default_autosave_formats = None
        # Load the defaults:
        self.__dict__.update(_FigureOptions._defaults)

        # Load the config file:
        if ScriptFlags.MREORG_MPLCONFIG_FILE:
            from configobj import ConfigObj
            config = ConfigObj(ScriptFlags.MREORG_MPLCONFIG_FILE, interpolation='template')
            config.interpolation = 'template'
            self.__dict__.update(config.get('options',{}))

    @property
    def is_draft(self):
        return self.draft
        #return False



FigureLayouts = _FigureLayouts()
FigureOptions = _FigureOptions()

