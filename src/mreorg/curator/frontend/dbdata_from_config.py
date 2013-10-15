#!/usr/bin/python
# -*- coding: utf-8 -*-

import models
from django.db import transaction
import os
import mreorg



@transaction.commit_on_success
def update_all_db(directory):

    print 'Updating untracked simulation files', directory
    for (dirpath, dirnames, filenames) in os.walk(directory):
        for filename in sorted(filenames):
            if not filename.endswith('.py'):
                continue
            print filename
            full_filename = os.path.join(dirpath, filename)
            if mreorg.MReOrgConfig.is_non_curated_file(filename):
                continue
            if mreorg.MReOrgConfig.is_non_curated_file(full_filename):
                continue

            print ' -- Adding:', filename
            models.SimFile.get_or_make( full_filename=full_filename, make_kwargs={'tracking_status':models.TrackingStatus.NotTracked})
            print 'Added OK!'


def update_db_from_config():
    import mreorg
    from mreorg.curator.frontend.models import RunConfiguration, FileGroup, SimFile
    from mreorg.curator.frontend.models import EnvironVar

    # Update the FileGroups:
    with transaction.commit_on_success():
        try:
            default_filegroups = mreorg.MReOrgConfig.config['CurateAutoloadData']['FileGroups']
        except KeyError:
            default_filegroups = {}

        #default_filegroups = mreorg.MReOrgConfig.get_ns().get('default_filegroups',{})
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

            print 'Updated FileGroup: %s' % (fgname, )

    # Update the RunConfigurations:
    with transaction.commit_on_success():
        try:
            default_runconfigs = mreorg.MReOrgConfig.config['CurateAutoloadData']['RunConfigs']
        except KeyError:
            default_runconfigs = {}
        #default_runconfigs = mreorg.MReOrgConfig.get_ns().get('default_runconfigs',{})
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

        # Add default locations:
        mh_adddefault_locations()
        # Rescan-filesystem:
        rescan_filesystem()

        # Cache docstring
        print 'Pre-Caching Docstrings:'
        for simfile in SimFile.objects.all():
            print simfile.full_filename
            simfile.get_docstring()

        print 'Finished Reconfiguring'


def rescan_filesystem():
    import dbdata_from_config

    with transaction.commit_on_success():
        for src_dir in models.SourceSimDir.objects.all():
            dbdata_from_config.update_all_db(src_dir.directory_name)



def mh_adddefault_locations():
    import mreorg
    default_simulations = mreorg.MReOrgConfig.config['Settings']['Curate']['default_tracked_simulations']

    with transaction.commit_on_success():
        for l in default_simulations:
            if not l:
                continue
            if l[-1] != '*':
                models.SimFile.get_or_make(full_filename=l, make_kwargs={'tracking_status': models.TrackingStatus.Tracked} )
            elif l.endswith('**'):
                models.SourceSimDir.create(directory_name=l[:-2],
                                    should_recurse=True)
            elif l.endswith('*'):
                models.SourceSimDir.create(directory_name=l[:-1],
                                    should_recurse=False)
            else:
                models.SourceSimDir.create(directory_name=l[:-2],
                                    should_recurse=False)


