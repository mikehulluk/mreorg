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

from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from mreorg.curator.frontend.models import SimFile
from mreorg.curator.frontend.models import SimQueueEntry
from mreorg.curator.frontend.models import SimRunStatus
from mreorg.curator.frontend.models import SimQueueEntryState
from mreorg.curator.frontend.models import RunConfiguration
from mreorg.curator.frontend.models import FileGroup
from django.db import transaction


def ensure_config():
    pass


@dajaxice_register
def base_set_runconfig(request, runconfig_id):
    runconfig = RunConfiguration.objects.get(id=int(runconfig_id))
    request.session['current_runconfig'] = runconfig
    return simplejson.dumps({})


@dajaxice_register
def base_set_filegroup(request, filegroup_id):
    filegroup = FileGroup.objects.get(id=int(filegroup_id))
    request.session['current_filegroup'] = filegroup
    return simplejson.dumps({})


@dajaxice_register
def overview_resubmit_simfile(_request, simfile_id):
    ensure_config()
    try:
        sim_file = SimFile.get_tracked_sims(id=simfile_id)
    except:
        return simplejson.dumps({})

    # Existing simulation object
    if not sim_file.simqueueentry_set.count():
        SimQueueEntry.create(
                sim_file=sim_file,
                runconfig=_request.session['current_runconfig'])
    return simplejson.dumps({})


@dajaxice_register
def overview_resubmit_simfile_if_failure(_request, simfile_id):
    try:
        sim_file = SimFile.get_tracked_sims(id=simfile_id)
    except:
        return simplejson.dumps({})

    if sim_file.get_status(runconfig=_request.session['current_runconfig']) == SimRunStatus.Success:
        return simplejson.dumps({})

    if not sim_file.simqueueentry_set.count():
        SimQueueEntry.create(sim_file=sim_file, runconfig=_request.session['current_runconfig'])

    return simplejson.dumps({})


@dajaxice_register
def overview_toggle_simfile_for_resubmit(_request, simfile_id):
    ensure_config()

    try:
        sim_file = SimFile.get_tracked_sims(id=simfile_id)
    except:
        return simplejson.dumps({})

    # Existing simulation object
    if sim_file.simqueueentry_set.count():
        sim_file.simqueueentry_set.all().delete()
    else:
        SimQueueEntry.create(sim_file=sim_file, runconfig=_request.session['current_runconfig'])

    return simplejson.dumps({})


@dajaxice_register
def refreshsimlist(_request):
    assert False, 'Is this used?'
    ensure_config()
    runconfig = _request.session['current_runconfig']
    states = {}
    for simfile in SimFile.get_tracked_sims():
        states[simfile.id] = simfile.get_status()
    return simplejson.dumps({'sim_file_states': states})





@dajaxice_register
def update_queue(_request, action):
    print 'Action', action
    tracked_sim_files = SimFile.get_tracked_sims()
    print 'Tracked sim files:', len(tracked_sim_files)

    runconfig=_request.session['current_runconfig']

    if action == 'add-all':
        with transaction.commit_on_success():
            for simfile in tracked_sim_files:
                if simfile.simqueueentry_set.count() > 0:
                    continue
                SimQueueEntry.create( sim_file=simfile, runconfig=runconfig)
        return simplejson.dumps({})

    if action == 'clear-all':
        SimQueueEntry.objects.all() .filter(status = SimQueueEntryState.Waiting).delete()
        return simplejson.dumps({})

    # TODO! Move functionality into here!
    if action == "add-all-failures":
        with transaction.commit_on_success():
            for simfile in tracked_sim_files:
                if simfile.simqueueentry_set.count() > 0:
                    continue
                if simfile.get_status(runconfig=runconfig) not in (SimRunStatus.TimeOut, SimRunStatus.UnhandledException, SimRunStatus.NonZeroExitCode, SimRunStatus.FileChanged,SimRunStatus.NeverBeenRun):
                    continue
                SimQueueEntry.create( sim_file=simfile, runconfig=_request.session['current_runconfig'])
        return simplejson.dumps({})

    if action == "add-all-failures-not-timeout":
        with transaction.commit_on_success():
            for simfile in tracked_sim_files:
                if simfile.simqueueentry_set.count() > 0:
                    continue
                if simfile.get_status(runconfig=runconfig) not in (SimRunStatus.UnhandledException, SimRunStatus.NonZeroExitCode, SimRunStatus.FileChanged,SimRunStatus.NeverBeenRun):
                    continue
                SimQueueEntry.create( sim_file=simfile, runconfig=_request.session['current_runconfig'])
        return simplejson.dumps({})



    else:
        assert False, 'Unhandled aciton: %s'% action
    print 'Action', action
    return simplejson.dumps({})


@dajaxice_register
def overview_update_sim_gui_batch(_request, simfile_ids):
    print 'Updating!'
    ensure_config()

    if isinstance(simfile_ids, int):
        simfile_ids = [simfile_ids]
    elif isinstance(simfile_ids, basestring):
        simfile_ids = [int(tok) for tok in simfile_ids.split()]
    else:
        assert False
    res = []
    for simfile_id in simfile_ids:

        try:
            sim_file = SimFile.get_tracked_sims(id=simfile_id)
        except SimFile.DoesNotExist:
            continue

        if not sim_file.does_file_exist():
            sim_file.delete()
            continue

        runconfig = _request.session['current_runconfig']
        last_run = sim_file.get_last_run(runconfig=runconfig)
        exec_date = last_run.execution_data_string() if last_run is not None else ""
        res.append(  {'sim_id':simfile_id,
                     'state':sim_file.get_status(runconfig=runconfig),
                     'is_queued':sim_file.is_queued(runconfig=runconfig),
                     'latest_exec_id':last_run.id if last_run else "",
                     'latest_exec_date': str(exec_date),
                     'latest_exec_duration': last_run.execution_time if last_run else '' ,
                    } ) 

    v = simplejson.dumps(res)
    print 'Retunrign from AJax'
    #print v
    return v





@dajaxice_register
def overview_update_sim_gui(_request, simfile_id):
    print 'Dajax call recieved', simfile_id
    from views import ensure_config
    ensure_config(_request)
    print 'A'
    sim_file = SimFile.get_tracked_sims(id=simfile_id)
    runconfig = _request.session['current_runconfig']
    print 'B'
    last_run = sim_file.get_last_run(runconfig=runconfig)
    print 'Bb'
    exec_date = last_run.execution_data_string() if last_run is not None else ""
    print 'C'
    v = simplejson.dumps(
                {'sim_id':simfile_id,
                 'state':sim_file.get_status(runconfig=runconfig),
                 'is_queued':sim_file.is_queued(runconfig=runconfig),
                 'latest_exec_id':last_run.id if last_run else "",
                 'latest_exec_date': exec_date,
                } )
    print 'Finsihed'
    return v


@dajaxice_register
def overview_clear_sim_queue(_request):
    SimQueueEntry.objects.all()\
            .filter(status = SimQueueEntryState.Waiting)\
            .delete()
    return simplejson.dumps({})

@dajaxice_register
def overview_delete_simfile(_request, simfile_id):
    ensure_config()

    try:
        sim_file = SimFile.get_tracked_sims(id=simfile_id)
        sim_file.delete()
    except:
        pass
    return simplejson.dumps({})
