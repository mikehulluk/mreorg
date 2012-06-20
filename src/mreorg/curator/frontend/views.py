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
from mreorg.curator.frontend.models import TrackedSimFile
from mreorg.curator.frontend.models import SimRunStatus
from mreorg.curator.frontend.models import SimFileRun
from mreorg.curator.frontend.models import SimQueueEntry
from mreorg.curator.frontend.models import SimQueueEntryState
from mreorg.curator.frontend.models import UntrackedSimFile
from mreorg.curator.frontend.models import SourceSimDir
from mreorg import MReOrgConfig
from django.template import RequestContext


import os
import re
import string
from urlparse import urlsplit

import os.path
import mimetypes
mimetypes.init()




def view_overview(request):
    return render_to_response(
            'overview.html',
            RequestContext(request, 
                {'simfiles': TrackedSimFile.objects.all()})
            )


def view_sim_output_summaries(request):
    sims = TrackedSimFile.objects.all()
    sim_and_dir = [(s, os.path.dirname(s.full_filename)) for s in sims]
    sim_and_dir.sort()

    sim_dirs = sorted(set([s[1] for s in sim_and_dir]))

    common_prefix = os.path.commonprefix(sim_dirs)

    output = []
    for sim_dir in sim_dirs:
        sd_short = '.../' + sim_dir.replace(common_prefix, '')
        sims_o = sorted([s[0] for s in sim_and_dir if s[1] == sim_dir],
                        key=lambda s: s.full_filename)
        output.append((sd_short, sims_o))

    cxt_data = {'simfiles': output}
    csrf_context = RequestContext(request, cxt_data)
    return render_to_response('simulation_output_summaries.html',
                              csrf_context)


def simfilerun_details(request, run_id):
    return render_to_response(
            'simulation_run_details.html',
            RequestContext(request, 
                {'simulationrun': SimFileRun.objects.get(id=run_id) } ) )



def simfile_details(request, simfile_id):
    sim = TrackedSimFile.objects.get(id=simfile_id)
    cxt_data = {'simfile': sim}
    csrf_context = RequestContext(request, cxt_data)
    return render_to_response('simfile_details.html',
                              csrf_context)



_have_run_update_tracking_locations = False


def view_tracking(request):
    global _have_run_update_tracking_locations

    # Update the default location files from the
    # config file:
    if not _have_run_update_tracking_locations:
        mh_adddefault_locations()
        _have_run_update_tracking_locations = True

    cxt_data = {'untracked_simfiles':UntrackedSimFile.objects.all(),
                'src_directories': SourceSimDir.objects.all(), 
                'simfiles': TrackedSimFile.objects.all()}
    csrf_context = RequestContext(request, cxt_data)
    return render_to_response('tracking.html',
                              csrf_context)


# Tracking Commands
# ====================
def do_track_all(request):
    for pot_sim in UntrackedSimFile.objects.all():
        sim = TrackedSimFile(full_filename=pot_sim.full_filename)
        sim.save()
        pot_sim.delete()

    return HttpResponseRedirect('/tracking')

def do_untrack_all(request):
    for sim in TrackedSimFile.objects.all():
        untr_sim = UntrackedSimFile(full_filename=sim.full_filename)
        untr_sim.save()
        sim.delete()

    return HttpResponseRedirect('/tracking')

def do_track_src_dir(request):
    if request.method != 'POST':
        return HttpResponseRedirect('/tracking')

    SourceSimDir.create(directory_name=request.POST['location'])
    return HttpResponseRedirect('/tracking')


def do_track_rescanfs(request):
    for src_dir in SourceSimDir.objects.all():
        UntrackedSimFile.update_all_db(src_dir.directory_name)
    return HttpResponseRedirect('/tracking')


def do_track_sim(request):
    if not request.method == 'POST':
        return HttpResponseRedirect('/tracking')


    # Find all keys matching untracked_sim_id_XX, and get the XX's

    r = re.compile(r"""untracked_sim_id_(?P<id>\d+)""", re.VERBOSE)
    pot_sim_id_matches = [r.match(k) for k in request.POST]
    pot_sim_ids = [int(m.groupdict()['id']) for m in pot_sim_id_matches if m]

    for pot_sim_id in pot_sim_ids:
        pot_sim = UntrackedSimFile.objects.get(id=pot_sim_id)

        sim = TrackedSimFile(full_filename=pot_sim.full_filename)

        sim.save()
        pot_sim.delete()

    return HttpResponseRedirect('/tracking')


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
        print 'Deleting', pot_sim_id
        sim = TrackedSimFile.objects.get(id=pot_sim_id)
        sim.delete()

    # Update the list of untracked files:
    return do_track_rescanfs(request)
    #return HttpResponseRedirect('/tracking')

# ====================






def viewsimulationqueue(request):
    cxt_data = \
        {'simulation_queue_executing': SimQueueEntry.objects.filter(status=SimQueueEntryState.Executing),
         'simulation_queue': SimQueueEntry.objects.filter(status=SimQueueEntryState.Waiting),
         'latest_runs': SimFileRun.objects.order_by('-execution_date'
         )[0:10]}

    csrf_context = RequestContext(request, cxt_data)
    return render_to_response('view_simulation_queue.html', csrf_context)


def view_simulation_failures(request):
    fileObjs = TrackedSimFile.objects.all()

    cxt_data = {
        'failed_simulations': [fo for fo in fileObjs if fo.get_status()
                               == SimRunStatus.UnhandledException],
        'timeout_simulations': [fo for fo in fileObjs
                                if fo.get_status()
                                == SimRunStatus.TimeOut],
        'nonzero_exitcode_simulations': [fo for fo in fileObjs
                if fo.get_status() == SimRunStatus.NonZeroExitCode],
        'changed_simulations': [fo for fo in fileObjs
                                if fo.get_status()
                                == SimRunStatus.FileChanged],
        'notrun_simulations': [fo for fo in fileObjs if fo.get_status()
                               == SimRunStatus.NeverBeenRun],
        }


    csrf_context = RequestContext(request, cxt_data)
    return render_to_response('view_simulation_failures.html',
                              csrf_context)


def doremovesimulationsfromqueue(request):
    return HttpResponseRedirect('/viewsimulationqueue')


def do_queue_add_sims(request):
    if not request.method == 'POST':
        return HttpResponseRedirect('/viewsimulationqueue')

    print 'Queuing Sims:'
    print request.POST
    r = re.compile(r"""simid_(?P<id>\d+)""", re.VERBOSE)
    sim_id_matches = [r.match(k) for k in request.POST]
    sim_ids = [int(m.groupdict()['id']) for m in sim_id_matches if m]

    for sim_id in sim_ids:
        sim = TrackedSimFile.objects.get(id=sim_id)

        qe = SimQueueEntry(simfile=sim)
        qe.save()

        # Avoid Duplication
    return HttpResponseRedirect('/viewsimulationqueue')
# ==================================






def doeditsimfile(request, simfile_id):

    #Open up the file in an editor:
    sim = TrackedSimFile.objects.get(id=simfile_id)

    cwd = os.getcwd()
    os.chdir( os.path.split(sim.full_filename)[0])
    data_dict = {'full_filename':sim.full_filename}
    cmds = MReOrgConfig.get_ns().get('drop_into_editor_cmds',['xterm &'])
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



def mh_adddefault_locations(self=None):
    default_simulations = \
        MReOrgConfig.get_ns().get('default_simulations', None)

    if not default_simulations:
        return HttpResponseRedirect('/')


    for l in default_simulations:
        if not l:
            continue
        if l[-1] != '*':
            UntrackedSimFile.create(filename=l)
        elif l.endswith('**'):
            SourceSimDir.create(directory_name=l[:-2],
                                should_recurse=True)
        elif l.endswith('*'):
            SourceSimDir.create(directory_name=l[:-1],
                                should_recurse=False)
        else:
            SourceSimDir.create(directory_name=l[:-2],
                                should_recurse=False)


def get_image_file(request, filename):
    print filename

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


