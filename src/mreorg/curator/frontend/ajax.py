#----------------------------------------------------------------------
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
#----------------------------------------------------------------------

from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from mreorg.curator.frontend.models import TrackedSimFile
from mreorg.curator.frontend.models import SimQueueEntry
from mreorg.curator.frontend.models import SimRunStatus
from mreorg.curator.frontend.models import SimQueueEntryState



@dajaxice_register
def overview_resubmit_simfile(_request, simfile_id):
    try:
        sim_file = TrackedSimFile.objects.get(id = simfile_id)
    except:
        #raise
        return simplejson.dumps({})


    # Existing simulation object
    if not sim_file.simqueueentry_set.count():
        SimQueueEntry.create( sim_file = sim_file )
    return simplejson.dumps({})


@dajaxice_register
def overview_resubmit_simfile_if_failure(_request, simfile_id):
#def overview_set_simfile_for_resubmit_if_failure(_request, simfile_id):
    try:
        sim_file = TrackedSimFile.objects.get(id = simfile_id)
        #raise
    except:
        return simplejson.dumps({})


    if sim_file.get_status() == SimRunStatus.Sucess:
        return simplejson.dumps({})

    if not sim_file.simqueueentry_set.count():
        SimQueueEntry.create( sim_file = sim_file )
    return simplejson.dumps({})



@dajaxice_register
def overview_toggle_simfile_for_resubmit(_request, simfile_id):

    try:
        sim_file = TrackedSimFile.objects.get(id = simfile_id)
        #raise
    except:
        return simplejson.dumps({})

    # Existing simulation object
    if sim_file.simqueueentry_set.count():
        sim_file.simqueueentry_set.all().delete()
    else:
        SimQueueEntry.create( sim_file = sim_file )
    return simplejson.dumps({})


@dajaxice_register
def refreshsimlist(_request):

    states = {}
    for simfile in TrackedSimFile.objects.all():
        states[simfile.id] = simfile.get_status()
    return simplejson.dumps({'sim_file_states':states})


@dajaxice_register
def overview_update_sim_gui(_request, simfile_id):
    print "Dajax call recieved", simfile_id
    sim_file = TrackedSimFile.objects.get(id = simfile_id)
    exec_date = ""
    if sim_file.get_latest_run():
        exec_date = sim_file.get_latest_run().execution_data_string()

    latest_run  = sim_file.get_latest_run()
    v = simplejson.dumps(
                {'sim_id':simfile_id,
                 'state':sim_file.get_status(),
                 'is_queued':sim_file.is_queued(),
                 'latest_exec_id':latest_run.id if latest_run else "",
                 'latest_exec_date': exec_date,
                } )
    return v



@dajaxice_register
def overview_clear_sim_queue(_request):
    SimQueueEntry.objects.all()\
            .filter(status = SimQueueEntryState.Waiting)\
            .delete()
    return simplejson.dumps({})

@dajaxice_register
def overview_delete_simfile(_request, simfile_id ):

    try:
        sim_file = TrackedSimFile.objects.get(id = simfile_id)
        sim_file.delete()
    except:
        pass
        #raise
    return simplejson.dumps({})
