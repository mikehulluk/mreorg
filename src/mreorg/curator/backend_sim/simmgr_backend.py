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

from django.core.management import setup_environ
import mreorg.curator.settings as settings
setup_environ(settings)

import time
import os
import datetime
import subprocess

from mreorg.curator.frontend.models import SimulationQueueEntry
from mreorg.curator.frontend.models import SimulationQueueEntryState


os.environ['MREORG_CURATIONRUN'] = 'TIMEOUT:1800,'
os.environ['MF_TIMEOUT'] = '1800'
os.environ['MF_TEST_COVERAGE'] = ''


def simulate( sim_queue_entry):
    filename = sim_queue_entry.simulation_file.full_filename
    print ' - Simulating: ', filename
    dname, fname = os.path.split(filename)

    # Update the database to reflect
    print '   - Updating database'
    sim_queue_entry.status = SimulationQueueEntryState.Executing
    sim_queue_entry.simulation_start_time = datetime.datetime.now()
    sim_queue_entry.save(force_update=True)


    # Simulate:
    print '   - Changing Directory to', dname
    os.chdir(dname)
    try:
        subprocess.check_call(["python", fname])
        print '   - Finished Simulating [Exit OK]'
    except subprocess.CalledProcessError as exception:
        print '   - Finished Simulating [Non-zero exitcode]'
        if not sim_queue_entry.simulation_file.get_latest_run():
            print 'Simulation not decorated! Unable to set return code'
        else:
            last_run = sim_queue_entry.simulation_file.get_latest_run()
            last_run.returncode = exception.returncode
            last_run.save(force_update=True)


    # Remove the sim_queue_entry:
    sim_queue_entry.delete()
    sim_queue_entry.simulation_file.recache_from_filesystem()



def main():
    while True:
        time.sleep(5)
        print 'Checking for Queued Simulations'

        queued_objects = SimulationQueueEntry.objects.\
                filter( status=SimulationQueueEntryState.Waiting).\
                order_by('submit_time')

        if not queued_objects:
            print ' - No Simulations found'
        else:
            simulate( queued_objects[0] )

main()
