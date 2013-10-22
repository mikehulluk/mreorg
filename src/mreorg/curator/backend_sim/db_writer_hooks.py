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

import sys
import os
import cStringIO
import time
import traceback
import datetime
import signal
import hashlib
import shutil
import pipes
import subprocess

# Setup django:
from django.core.management import setup_environ
import mreorg.curator.settings as settings
setup_environ(settings)

import mreorg
from mreorg.utils import get_file_sha1hash
from mreorg.curator.frontend.models import SimFileRun
from mreorg.curator.frontend.models import SimFile
from mreorg.curator.frontend.models import SimFileRunOutputImage
from mreorg.curator.frontend.models import RunConfiguration
from mreorg.curator.frontend.models import TrackingStatus
from django.db import transaction


class SimDBWriter(object):

    @classmethod
    def write_to_database(cls, sim_run_info):
        output_file_dir = mreorg.MReOrgConfig.get_image_store_dir()

        print 'Saving details from script: ', sim_run_info.script_name

        # We don't neeed to update this file every time:
        if mreorg.MReOrgConfig.is_non_curated_file(sim_run_info.script_name):
            return


        simfile = SimFile.get_or_make(full_filename=sim_run_info.script_name, make_kwargs={'tracking_status':TrackingStatus.Tracked})
        

        import time

        # Create a simulation result object:
        simres = SimFileRun(
            simfile=simfile,
            execution_date=datetime.datetime.now(),
            execution_time=sim_run_info.time_taken,
            return_code=sim_run_info.return_code,
            std_out=sim_run_info.std_out,
            std_err=sim_run_info.std_err,
            exception_type=sim_run_info.exception_details[0],
            exception_traceback=str(sim_run_info.exception_details[2]),
            simulation_sha1hash=get_file_sha1hash(simfile.full_filename),
            library_sha1hash='00000',
            runconfig=RunConfiguration.objects.get(id=int(os.environ['_MREORG_RUNCONFIGID'])),
            )

        simres.save()

        with transaction.commit_on_success():
            output_file_dir = mreorg.MReOrgConfig.get_image_store_dir()
            # Create the images
            for image_filename in sim_run_info.output_images:
                if not image_filename.endswith('svg'):
                    continue

                # Copy the output file:
                try:
                    hashstr = mreorg.get_file_sha1hash(image_filename)
                except:
                    hashstr = None

                if hashstr == None:
                    continue

                opfile1 = output_file_dir + '/' + hashstr + '.svg'
                shutil.copyfile(image_filename, opfile1)

                f_thumb = image_filename.replace('.svg', 'thumb.png')
                os.system('convert %s -resize 400x300 %s' % (pipes.quote(image_filename),pipes.quote(f_thumb)))
                time.sleep(5) # Sometimes, its not ready!
                #hashstr = hashlib.md5(open(f_thumb).read()).hexdigest()
                hashstr = mreorg.get_file_sha1hash(f_thumb)
                opfile2 = output_file_dir + '/' + hashstr + ".png"
                shutil.copyfile(f_thumb, opfile2)
                im_obj = SimFileRunOutputImage(
                        original_name=image_filename,
                        hash_name=opfile1,
                        hash_thumbnailname=opfile2,
                        simulation=simres)


                im_obj.save()


class SimRunInfo(object):

    def __init__(self, script_name):
        self.return_code = None
        self.time_taken = None
        self.time_out = None
        self.std_out = None
        self.std_err = None
        self.exception_details = (None, None)

        self.script_name = script_name
        self.output_images = []


class IOStreamDistributor(object):

    def __init__(self, outputs):
        self.outputs = outputs

    def write(self, *args, **kwargs):
        for output in self.outputs:
            output.write(*args, **kwargs)

    def flush(self):
        for output in self.outputs:
            try:
                output.flush()
            except:
                pass


class TimeoutException(Exception):

    def __init__(self, timeout):
        super(TimeoutException, self).__init__()
        self.timeout = timeout

    def __repr__(self):
        return 'TImeoutException (%ds)' % self.timeout

    def __str__(self):
        return 'TImeoutException (%ds)' % self.timeout


class CurationSimDecorator(object):

    start_time = None
    time_out = None
    is_initialised = False
    exception_details = (None, None, None)

    std_out = None
    std_err = None
    script_name = None

    @classmethod
    def exit_handler(cls, *_args, **_kwargs):

        info = SimRunInfo(cls.script_name)

        # Read and restore the StdOut/Err
        info.std_out = cls.std_out.getvalue()
        sys.stdout = sys.__stdout__
        info.std_err = cls.std_err.getvalue()
        sys.stderr = sys.__stderr__

        # Pick-up any saved images:
        mreorg.PlotManager.save_active_figures()
        info.output_images = mreorg.PlotManager.figures_saved_filenames

        # Get the return value:
        info.return_code = 0

        # Get the timing:
        info.time_taken = int(time.time() - cls.start_time)

        # Has there been an exception?
        info.exception_details = cls.exception_details
        if info.exception_details != (None, None, None):
            print 'Exception details', info.exception_details
            info.return_code = -1

        # Write to SimDataBase
        SimDBWriter.write_to_database(info)

    @classmethod
    def top_level_exception_handler(cls, exception_type, exception, tracebackobj, *_args):
        try:
            traceback_str = str(exception) +'\n'+ ''.join(traceback.format_tb(tracebackobj))

            print ''
            print 'TopLevel-Handler Caught Exception:'
            print '----------------------------------'
            print traceback_str
            cls.exception_details = exception_type, exception, traceback_str
            cls.exit_handler()
        except Exception, exception:
            print 'INTERNAL ERROR, exception raised in top level handler!'
            print exception
            sys.exit(0)

    @classmethod
    def activate(cls, time_out=None):
        assert not cls.is_initialised

        if 'MREORG_TIMEOUT' in os.environ:
            time_out = int(os.environ['MREORG_TIMEOUT'])

        # Filename of the Sim script
        cwd = os.getcwd()
        cls.script_name = os.path.join(cwd, traceback.extract_stack()[0][0])

        # Intercept StdOut and StdErr:
        cls.std_out = cStringIO.StringIO()
        sys.stdout = IOStreamDistributor([cls.std_out, sys.stdout])
        cls.std_err = cStringIO.StringIO()
        sys.stderr = IOStreamDistributor([cls.std_err, sys.stderr])

        # Set an exit handler
        from mreorg.atexithandlers import AtExitHandler
        AtExitHandler.add_handler(cls.exit_handler, 100)

        # Set a top level exception handler:
        sys.excepthook = cls.top_level_exception_handler

        # Set a time-out alarm
        cls.start_time = time.time()
        cls.time_out = time_out

        def timeout_sighandler(_signum, _frame):
            raise TimeoutException(timeout=cls.time_out)

        if time_out:
            signal.signal(signal.SIGALRM, timeout_sighandler)
            signal.alarm(time_out)


