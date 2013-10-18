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

from django.core.management import setup_environ
import mreorg.curator.settings as settings
setup_environ(settings)
import django

import time
import os
import datetime
import subprocess
import sys
import signal
import random

from mreorg.curator.frontend.models import SimQueueEntry
from mreorg.curator.frontend.models import SimQueueEntryState
import mreorg


def simulate(sim_queue_entry):
    filename = sim_queue_entry.simfile.full_filename
    print ' - Simulating: ', filename
    (dname, fname) = os.path.split(filename)

    # Update the database to reflect
    print '   - Updating database'
    sim_queue_entry.status = SimQueueEntryState.Executing
    sim_queue_entry.simulation_start_time = datetime.datetime.now()
    sim_queue_entry.simulation_last_heartbeat = datetime.datetime.now()
    sim_queue_entry.save(force_update=True)

    def try_heartbeat():
        try:
            sim_queue_entry.simulation_last_heartbeat = datetime.datetime.now()
            sim_queue_entry.save(force_update=True)
        except django.db.utils.DatabaseError:
            pass

    # First heartbeat:
    try_heartbeat()

    # Setup the environmental variables:
    # Pass the RunConfiguration.id as an environmental variable

    os.environ['_MREORG_RUNCONFIGID'] = str(sim_queue_entry.runconfig.id)

    if sim_queue_entry.runconfig.timeout:
        os.environ['MREORG_CONFIG'] =os.environ.get('MREORG_CONFIG') + ';TIMEOUT=%d' % sim_queue_entry.runconfig.timeout

    for envvar in sim_queue_entry.runconfig.environvar_set.all():
        key = envvar.key
        value = envvar.value
        if value is None:
            if key in os.environ:
                del os.environ[key]
        else:
            os.environ[key] = value

    # Setup the heartbeat, to say that we are actually alive:
    heartbeat_interval = mreorg.MReOrgConfig.config['Settings']['Curate']['backend_heartbeat_rate']

    def handler(*args, **kwargs):
        signal.alarm(heartbeat_interval)
        try_heartbeat()

    signal.alarm(heartbeat_interval)
    signal.signal(signal.SIGALRM, handler)

    # Simulate:
    print '   - Changing Directory to', dname
    os.chdir(dname)
    try:
        subprocess.check_call(['python', fname])
        print '   - Finished Simulating [Exit OK]'
    except subprocess.CalledProcessError, exception:
        print '   - Finished Simulating [Non-zero exitcode]'
        last_run = sim_queue_entry.simfile.get_last_run(sim_queue_entry.runconfig)
        if not last_run:
            print 'Sim not decorated! Unable to set return code'
        else:
            last_run.returncode = exception.returncode
            last_run.save(force_update=True)

    # Turn off heartbeating.
    signal.alarm(0)
    try_heartbeat()

    # Remove the sim_queue_entry:
    sim_queue_entry.delete()
    sim_queue_entry.simfile.recache_from_filesystem()


def _run_backend():

    os.environ['MREORG_CONFIG']=os.environ.get('MREORG_CONFIG','') + ';CURATIONRUN'
    os.environ['MREORG_CONFIG']=os.environ.get('MREORG_CONFIG','') + ';ENABLECOVERAGE'


    while True:

        print '\r Checking for Queued Sims: ', time.strftime('%l:%M%p (%S) on %b %d, %Y'),
        sys.stdout.flush()
        queued_objects = SimQueueEntry.objects.\
                filter(status=SimQueueEntryState.Waiting).\
                order_by('submit_time')

        if queued_objects:
            print
            simulate(queued_objects[0])
            print

        time.sleep(random.randint(3,20))

def run_backend():
    try:
        _run_backend()
    except KeyboardInterrupt:
        print 'Stopping'


if __name__ == '__main__':
    run_backend()

