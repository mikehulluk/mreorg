#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
# Copyright (cxt_data) 2012 Michael Hull.
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

from django.shortcuts import render_to_response

from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.http import HttpResponse
from mreorg.curator.frontend.models import SimFile
from mreorg.curator.frontend.models import SimRunStatus
from mreorg.curator.frontend.models import SimFileRun
from mreorg.curator.frontend.models import SimQueueEntry
from mreorg.curator.frontend.models import SimQueueEntryState
from mreorg.curator.frontend.models import SourceSimDir
from mreorg.curator.frontend.models import RunConfiguration
from mreorg.curator.frontend.models import FileGroup
from mreorg.curator.frontend.models import TrackingStatus
from mreorg import MReOrgConfig
from django.template import RequestContext
from dbdata_from_config import rescan_filesystem

import os
import re
import string
from urlparse import urlsplit

import os.path
import mimetypes
mimetypes.init()

from django.db import transaction


def ensure_config(request):
    if not 'current_runconfig' in request.session:
        request.session['current_runconfig'] = RunConfiguration.get_initial()
    if not 'current_filegroup' in request.session:
        request.session['current_filegroup'] = FileGroup.get_initial()


def config_processor(request):
    ensure_config(request)

    return {
        'runconfigs': RunConfiguration.objects.all(),
        'filegroups': FileGroup.objects.all(),
        'current_runconfig': request.session['current_runconfig'],
        'current_filegroup': request.session['current_filegroup'],
        }


class SimFileWithRunConfigProxy(object):

    def __init__(self, simfile, runconfig):
        self.simfile = simfile
        self.runconfig = runconfig

        self._does_file_exist = self.simfile.does_file_exist()
        self._get_docstring= self.simfile.get_docstring()
        self._get_short_filename= self.simfile.get_short_filename()
        self._get_status= self.simfile.get_status(runconfig=self.runconfig)
        self._get_last_executiontime= self.simfile.get_last_executiontime(runconfig=self.runconfig)
        self._is_queued= self.simfile.is_queued(runconfig=self.runconfig)
        self._getCSSQueueState= self.simfile.getCSSQueueState(runconfig=self.runconfig)
        self._full_filename= self.simfile.full_filename
        self._id= self.simfile.id
        self._tracking_status= self.simfile.tracking_status
        self._get_last_run= self.simfile.get_last_run(runconfig=self.runconfig)
        self._is_currently_running= self.simfile.is_currently_running(self.runconfig)


    def does_file_exist(self):
        return self._does_file_exist

    def get_docstring(self):
        return self._get_docstring

    def get_short_filename(self):
        return self._get_short_filename

    def get_status(self):
        return self._get_status

    def get_last_executiontime(self):
        return self._get_last_executiontime

    def is_queued(self):
        return self._is_queued

    def getCSSQueueState(self):
        return self._getCSSQueueState

    @property
    def full_filename(self):
        return self._full_filename

    @property
    def id(self):
        return self._id

    @property
    def tracking_status(self):
        return self._tracking_status

    def get_last_run(self):
        return self._get_last_run
    
    def is_currently_running(self):
        return self._is_currently_running

    def __getattr__(self, name):
        print 'looking for attribute:', name
        assert False















def build_proxy_for_sim_files(simfiles, runconfig):
    return [SimFileWithRunConfigProxy(sim,runconfig) for sim in simfiles if sim.does_file_exist()]




def view_overview(request):
    ensure_config(request)

    sims = build_proxy_for_sim_files( request.session['current_filegroup'].tracked_files, runconfig= request.session['current_runconfig'] )
    return render_to_response(
            'overview.html',
            RequestContext(request,
                { 'simfiles': sims },
                [config_processor]
                )
            )

def view_sim_output_summaries(request):
    ensure_config(request)
    sims = build_proxy_for_sim_files( request.session['current_filegroup'].tracked_files, runconfig= request.session['current_runconfig'] )
    cxt_data = {'simfiles':sims}
    csrf_context = RequestContext(request, cxt_data, [config_processor] )
    return render_to_response('simulation_output_summaries.html', csrf_context)


def view_configurations(request):
    ensure_config(request)

    cxt_data = {}
    csrf_context = RequestContext(request, cxt_data, [config_processor])
    return render_to_response('configurations.html', csrf_context)


def simfilerun_details(request, run_id):
    return render_to_response(
            'simulation_run_details.html',
            RequestContext(request,
                {'simulationrun': SimFileRun.objects.get(id=run_id) },
                [config_processor] ) )



def simfile_details(request, simfile_id):
    sim_file = SimFile.get_tracked_sims(id=simfile_id)
    cxt_data = {'simfile': sim_file}
    csrf_context = RequestContext(request, cxt_data)
    return render_to_response('simfile_details.html', csrf_context)


def view_tracking(request):

    cxt_data = {'src_directories': SourceSimDir.objects.all(),
                'untracked_simfiles': SimFile.get_untracked_sims(),
                'simfiles': SimFile.get_tracked_sims()}
    csrf_context = RequestContext(request, cxt_data, [config_processor])
    return render_to_response('tracking.html', csrf_context)


# Tracking Commands
# ====================

@transaction.commit_on_success
def do_track_all(request):
    for sim in SimFile.get_untracked_sims():
        sim.tracking_status = TrackingStatus.Tracked
        sim.save()
    return HttpResponseRedirect('/tracking')


@transaction.commit_on_success
def do_untrack_all(request):
    for sim in SimFile.get_tracked_sims():
        sim.tracking_status = TrackingStatus.NotTracked
        sim.save()

    return HttpResponseRedirect('/tracking')


def do_track_src_dir(request):
    if request.method != 'POST':
        return HttpResponseRedirect('/tracking')

    SourceSimDir.create(directory_name=request.POST['location'],
			should_recurse='recurse' in request.POST)
    return HttpResponseRedirect('/tracking')


def do_untrack_src_dir(request, srcdir_id):
    o = SourceSimDir.objects.get(id=srcdir_id)
    o.delete()
    return HttpResponseRedirect('/tracking')


def do_track_rescanfs(request):
    rescan_filesystem()
    return HttpResponseRedirect('/tracking')


@transaction.commit_on_success
def do_track_sim(request):
    if not request.method == 'POST':
        return HttpResponseRedirect('/tracking')

    # Find all keys matching untracked_sim_id_XX, and get the XX's

    r = re.compile(r"""untracked_sim_id_(?P<id>\d+)""", re.VERBOSE)
    pot_sim_id_matches = [r.match(k) for k in request.POST]
    pot_sim_ids = [int(m.groupdict()['id']) for m in pot_sim_id_matches if m]

    for pot_sim_id in pot_sim_ids:
        sim = SimFile.objects.get(id=pot_sim_id)
        sim.tracking_status = TrackingStatus.Tracked
        sim.save()

    return HttpResponseRedirect('/tracking')


@transaction.commit_on_success
def do_untrack_sim(request):
    if not request.method == 'POST':
        return HttpResponseRedirect('/tracking')

    # Find all keys matching untracked_sim_id_XX, and get the XX's
    print request.POST.keys()
    r = re.compile(r"""simid_(?P<id>\d+)""", re.VERBOSE)
    pot_sim_id_matches = [r.match(k) for k in request.POST]
    pot_sim_ids = [int(m.groupdict()['id']) for m in pot_sim_id_matches
                   if m]

    # Delete the old simulations:
    for pot_sim_id in pot_sim_ids:
        sim = SimFile.objects.get(id=pot_sim_id)
        sim.tracking_status = TrackingStatus.NotTracked
        sim.save()

    # Update the list of untracked files:
    return do_track_rescanfs(request)


# ====================

def viewsimulationqueue(request):
    cxt_data = \
        {'simulation_queue_executing': SimQueueEntry.objects.filter(status=SimQueueEntryState.Executing),
         'simulation_queue': SimQueueEntry.objects.filter(status=SimQueueEntryState.Waiting),
         'latest_runs': SimFileRun.objects.order_by('-execution_date')[0:10]}

    SimQueueEntry.trim_dangling_jobs()

    csrf_context = RequestContext(request, cxt_data)
    return render_to_response('view_simulation_queue.html', csrf_context)


def view_simulation_failures(request):
    ensure_config(request)
    runconfig= request.session['current_runconfig']
    simfiles = build_proxy_for_sim_files(SimFile.get_tracked_sims(), runconfig=runconfig)
    cxt_data = {
        'failed_simulations': [fo for fo in simfiles if fo.get_status() == SimRunStatus.UnhandledException],
        'timeout_simulations': [fo for fo in simfiles if fo.get_status() == SimRunStatus.TimeOut],
        'nonzero_exitcode_simulations': [fo for fo in simfiles if fo.get_status() == SimRunStatus.NonZeroExitCode],
        'changed_simulations': [fo for fo in simfiles if fo.get_status() == SimRunStatus.FileChanged],
        'notrun_simulations': [fo for fo in simfiles if fo.get_status() == SimRunStatus.NeverBeenRun],
        }


    csrf_context = RequestContext(request, cxt_data, [config_processor])
    return render_to_response('view_simulation_failures.html',
                              csrf_context)



def doremovesimulationsfromqueue(request):
    return HttpResponseRedirect('/viewsimulationqueue')


def do_queue_add_sims(request):
    ensure_config(request)
    if not request.method == 'POST':
        return HttpResponseRedirect('/viewsimulationqueue')

    print 'Queuing Sims:'
    print request.POST
    r = re.compile(r"""simid_(?P<id>\d+)""", re.VERBOSE)
    sim_id_matches = [r.match(k) for k in request.POST]
    sim_ids = [int(m.groupdict()['id']) for m in sim_id_matches if m]

    runconfig = request.session['current_runconfig']

    for simfile_id in sim_ids:
        sim_file = SimFile.get_tracked_sims(id=simfile_id)

        qe = SimQueueEntry(simfile=sim_file, runconfig=runconfig)
        qe.save()

        # Avoid Duplication
    return HttpResponseRedirect('/viewsimulationqueue')



def doeditsimfile(request, simfile_id):

    # Open up the file in an editor:
    sim_file = SimFile.get_tracked_sims(id=simfile_id)

    cwd = os.getcwd()
    os.chdir(os.path.split(sim_file.full_filename)[0])
    data_dict = {'full_filename': sim_file.full_filename}
    #cmds = MReOrgConfig.get_ns().get('drop_into_editor_cmds', ['xterm &'])
    #cmds = MReOrgConfig.get_ns().get('drop_into_editor_cmds', ['xterm &'])
    #cmds = MReOrgConfig.get_ns().get('drop_into_editor_cmds', ['xterm &'])
    cmds = MReOrgConfig.config['Settings']['Curate']['drop_into_editor_cmds']
    for cxt_data in cmds:
        t = string.Template(cxt_data).substitute(**data_dict)
        os.system(t)
    os.chdir(cwd)

    # Return to the previous page:
    referer = request.META.get('HTTP_REFERER', None)
    if referer is None:
        return HttpResponseRedirect('/')

    try:
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)
    except IndexError:
        return HttpResponseRedirect('/')


def get_image_file(request, filename):

    im_dir = MReOrgConfig.get_image_store_dir()

    expected_filename = os.path.join(im_dir, filename)

    if os.path.exists(expected_filename):

        fsock = open(expected_filename, 'r')
        file_path = expected_filename
        file_name = os.path.basename(file_path)
        mime_type_guess = mimetypes.guess_type(file_name)
        if mime_type_guess is not None:
            response = HttpResponse(fsock, mimetype=mime_type_guess[0])
        response['Content-Disposition'] = 'attachment; filename=' \
            + file_name
        return response
    else:
        return HttpResponseNotFound('<h1>Image not found</h1>')
    assert False


