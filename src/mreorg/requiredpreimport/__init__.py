import os





# Query Settings:
def showGUI():
    if os.environ.get('MF_PLOT',None) == 'OFF':
        return False
    if os.environ.get('MF_BATCH',None):
        return False
    return  True





on_rtd = os.environ.get('READTHEDOCS', None) == 'True'
if not on_rtd:

    # Matplotlib:
    import matplotlib
    if not os.environ.get('DISPLAY',None):
        matplotlib.use('Agg')


    # patch mpl.show()
    import pylab
    mplShow = matplotlib.pylab.show
    def show(*args, **kwargs):
        import mreorg.scriptplots.plotmanager
        mreorg.scriptplots.plotmanager.saveAllNewActiveFigures()
        if showGUI():
            #LogMgr.info("mpl.show() call made")
            mplShow(*args, **kwargs)

        else:
            pass
            #LogMgr.info("mpl.show() call not made")
    matplotlib.pylab.show = show
    pylab.show = show


    # patch mpl.savefig
    #  - Make sure that the directory actually exists:
    mplsavefig = matplotlib.pylab.savefig
    def savefig(filename, *args, **kwargs):
        print 'Custom Savefig:'
        dirname = os.path.dirname(filename)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname)
        return mplsavefig(filename, *args, **kwargs)
    matplotlib.pylab.savefig = savefig
    pylab.savefig = savefig




# Hook in the coverage
if "MF_TEST_COVERAGE" in os.environ:
    #assert False
    coverage_opdir = '/tmp/morphforge_coverage_output'
    if not os.path.exists(coverage_opdir):
        os.makedirs(coverage_opdir)
    os.environ['COVERAGE_PROCESS_START']="/home/michael/hw_to_come/morphforge/etc/.coveragerc"
    import coverage
    coverage.process_startup()





def DecorateSimulations():
    if os.environ.get('MF_BATCH',None):
            return True
    return False

if DecorateSimulations():
    print 'Decorating Simulation'
    from mreorg.curator.backend_sim.db_writer_hooks import SimulationDecorator
    SimulationDecorator.Init()







