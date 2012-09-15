

def from_default_monitor_dirs():
    #default_filegroups = mreorg.MReOrgConfig.get_ns().get('default_filegroups',{})
    #for fgname, fgglobs in default_filegroups.iteritems():
    pass



def update_db_from_config():
    import mreorg
    from mreorg.curator.frontend.models import RunConfiguration, FileGroup, SimFile
    from mreorg.curator.frontend.models import EnvironVar

    # Update the FileGroups:
    default_filegroups = mreorg.MReOrgConfig.get_ns().get('default_filegroups',{})
    for fgname, fgglobs in default_filegroups.iteritems():
        filenames = set()
        for fgglob in fgglobs:
            filenames.update(mreorg.glob2.glob(fgglob) )

        # Safely get the FileGroup:
        fg = FileGroup.get_or_make(name=fgname)
        assert not fg.is_special(), 'Trying to overwrite a builtin filegroup'
        for filename in filenames:
            simfile = SimFile.get_or_make(full_filename=filename)
            if not fg.contains_simfile(simfile):
                fg.simfiles.add(simfile)
                fg.save()

        print 'Updated FileGroup: %s' % (fgname,)


    # Update the RunConfigurations:
    default_runconfigs = mreorg.MReOrgConfig.get_ns().get('default_runconfigs',{})
    for confname, confinfo in default_runconfigs.iteritems():
        runconf = RunConfiguration.get_or_make(name=confname)
        assert not runconf.is_special(), 'Trying to add a builtin-configuration'
        runconf.timeout = confinfo.get('timeout',None)

        for (key, value) in confinfo.get('env_vars',{}).iteritems():
            try:
                envvar = runconf.environvar_set.get(key=key)
                envvar.value = value
                envvar.save()
            except EnvironVar.DoesNotExist:
                envvar = EnvironVar(key=key,value=value,config=runconf)
                envvar.save()

        runconf.save()
        print 'Updated RunConfig: %s' % confname




def mh_adddefault_locations():
    default_simulations = MReOrgConfig.get_ns().get('default_simulations', None)

    if not default_simulations:
        return HttpResponseRedirect('/')


    for l in default_simulations:
        if not l:
            continue
        if l[-1] != '*':
            SimFile.create(full_filename=l, tracked=False)
        elif l.endswith('**'):
            SourceSimDir.create(directory_name=l[:-2],
                                should_recurse=True)
        elif l.endswith('*'):
            SourceSimDir.create(directory_name=l[:-1],
                                should_recurse=False)
        else:
            SourceSimDir.create(directory_name=l[:-2],
                                should_recurse=False)
