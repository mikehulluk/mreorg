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
import os
import datetime
import StringIO

from django.db import models
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

import mreorg


class Options(object):

    MinimumFileCheckInterval = datetime.timedelta(minutes=5)


class SourceSimDir(models.Model):

    class Meta:

        ordering = ['directory_name']

    directory_name = models.CharField(max_length=1000)
    should_recurse = models.BooleanField()

    def does_exist(self):
        return os.path.exists(self.directory_name)

    @classmethod
    def create(cls, directory_name, should_recurse=True):
        directory_name = os.path.normpath(directory_name)
        if SourceSimDir.objects.filter(directory_name=directory_name).count() !=0:
            return

        # Create and save
        p = SourceSimDir(directory_name=directory_name, should_recurse=should_recurse)
        p.save()


class TrackingStatus(object):

    Tracked = 'Tracked'
    NotTracked = 'Nottracked'


class SimFile(models.Model):

    class Meta:
        ordering = ['full_filename']

    @classmethod
    def get_or_make(self, full_filename, make_kwargs=None):
        full_filename = os.path.expanduser(full_filename)

        try:
            simfile = SimFile.objects.get(full_filename=full_filename)
        except SimFile.DoesNotExist:
            make_kwargs = make_kwargs or {}
            simfile = SimFile(full_filename=full_filename, **make_kwargs)
            simfile.save()
        return simfile




    full_filename = models.CharField(max_length=1000)
    tracking_status = models.CharField(
            max_length=1000,
            default=TrackingStatus.NotTracked,
            choices= [
                (TrackingStatus.Tracked,TrackingStatus.Tracked),
                (TrackingStatus.NotTracked,TrackingStatus.NotTracked),
                ] )

    # We cache the docstring, the code, code rendered as HTML:
    last_read_sha1 = models.CharField(max_length=100000, null=True)
    last_read_time = models.DateTimeField(null=True)
    last_read_contents = models.CharField(max_length=100000, null=True)
    last_read_docstring = models.CharField(max_length=100000, null=True)
    last_read_htmlcode = models.CharField(max_length=100000, null=True)

    # Last simulation run:
    #last_run = models.ForeignKey('SimFileRun',null=True, related_name='+')

    @classmethod
    def get_tracked_sims(cls, **kwargs):
        if kwargs:
            return SimFile.objects.get(tracking_status=TrackingStatus.Tracked, **kwargs)
        return SimFile.objects.filter(tracking_status=TrackingStatus.Tracked)

    @classmethod
    def get_untracked_sims(cls,**kwargs):
        if kwargs:
            return SimFile.objects.get(tracking_status=TrackingStatus.NotTracked, **kwargs)
        return SimFile.objects.filter(tracking_status=TrackingStatus.NotTracked)


    # Handle Caching:
    # ##########################################
    def _is_cache_valid(self):
        if not self.last_read_time:
            return False
        # We only maximally recalculate the hash every so often:
        if self.last_read_time - datetime.datetime.now() < Options.MinimumFileCheckInterval:
            return True
        if self.get_current_checksum() == self.last_read_sha1:
            return True
        return False

    def recache_from_filesystem(self):
        print 'Recaching: ', self.full_filename
        with open(self.full_filename) as f:
            code = f.read()

        self.last_read_sha1 = self.get_current_checksum()
        self.last_read_time = datetime.datetime.now()
        self.last_read_contents  = code
        self.last_read_docstring = mreorg.utils.extract_docstring_from_fileobj(StringIO.StringIO( code ) )
        self.last_read_htmlcode = highlight(code, PythonLexer(), HtmlFormatter())
        self.save()


    def check_and_recache(self):
        if not self._is_cache_valid():
            self.recache_from_filesystem()
    # ##########################################



    def does_file_exist(self):
        return os.path.exists(self.full_filename)


    def get_html_code(self):
        self.check_and_recache()
        return self.last_read_htmlcode

    def get_docstring(self):
        self.check_and_recache()
        return self.last_read_docstring

    def _get_last_run(self, runconfig):
        runs = self.get_runs(runconfig=runconfig)
        if len(runs) == 0:
            return None
        else:
            return self.get_runs(runconfig=runconfig)[0]

    def get_last_run(self, runconfig):
        if runconfig.id not in self.latest_run_dict:
            self.latest_run_dict[runconfig.id] = self._get_last_run(runconfig)
        return self.latest_run_dict[runconfig.id]


    def get_current_checksum(self):
        return mreorg.get_file_sha1hash(self.full_filename)

    def get_short_filename(self):
        return os.path.split(self.full_filename)[1]

    def get_runs(self, runconfig):
        return SimFileRun.objects. \
                    filter(simfile=self.id, runconfig=runconfig). \
                    order_by('-execution_date')


    def get_status(self, runconfig):
        last_run = self.get_last_run(runconfig)
        if not last_run:
            return SimRunStatus.NeverBeenRun
        else:
            return last_run.get_status()

    def get_last_executiontime(self, runconfig):
        last_run = self.get_last_run(runconfig)
        if not last_run:
            return 'Unknown'
        else:
            return last_run.execution_time

    def is_queued(self, runconfig):
        return self.simqueueentry_set.filter(runconfig=runconfig).count() != 0

    def getCSSQueueState(self, runconfig):
        p = self.is_queued(runconfig=runconfig)
        LUT = {True: 'SimQueued', False: 'SimNotQueued'}
        return LUT[p]


    def is_currently_running(self,runconfig):
        #print 'Lying about whether I am currently running'
        return False



def extra_init_for_simfile(instance, **kwargs):
    #print 'extra init for simfile', kwargs
    instance.latest_run_dict = {}


from django.db.models.signals import post_init
post_init.connect(extra_init_for_simfile, SimFile)     



class RunConfiguration(models.Model):

    special_configs = ['default']

    @classmethod
    def get_or_make(self, name, make_kwargs=None):
        try:
            runconf = RunConfiguration.objects.get(name=name)
        except RunConfiguration.DoesNotExist:
            if make_kwargs is None:
                make_kwargs = {}
            runconf = RunConfiguration(name=name, **make_kwargs)
            runconf.save()
        return runconf

    class Meta:

        ordering = ('name', )

    name = models.CharField(max_length=10000000)
    timeout = models.IntegerField(null=True)

    def is_special(self):
        return self.name in RunConfiguration.special_configs

    @classmethod
    def build_all_specials(cls):
        for special_name in RunConfiguration.special_configs:
            rc = cls.get_or_make(special_name)
            assert rc.is_special()
            rc.save()

    @classmethod
    def get_initial(cls):
        return cls.get_or_make(name='default')


class FileGroup(models.Model):

    special_groups = ['all']

    class Meta:

        ordering = ('name', )

    name = models.CharField(max_length=10000000)
    simfiles = models.ManyToManyField(SimFile)

    @classmethod
    def get_or_make(self, name):
        try:
            fg = FileGroup.objects.get(name=name)
        except FileGroup.DoesNotExist:
            fg = FileGroup(name=name)
            fg.save()
        return fg

    def is_special(self):
        return self.name in FileGroup.special_groups

    def display_name(self):
        if self.is_special():
            return '--%s--' % self.name
        else:
            return self.name

    def contains_simfile(self, simfile):
        print 'Does', self.name, 'contain', simfile.full_filename, '?'
        if self.name == 'all':
            return True

        assert not self.is_special(), 'NotImplementedYet'
        res = self.simfiles.filter(id=simfile.id).count() > 0
        return res

    @classmethod
    def build_all_specials(cls):
        for special_name in FileGroup.special_groups:
            rc = cls.get_or_make(special_name)
            assert rc.is_special()
            rc.save()

    @classmethod
    def get_initial(cls):
        return cls.get_or_make(name='all')

    @property
    def tracked_sims(self):
        return self.tracked_files

    @property
    def tracked_files(self):
        if self.is_special():
            if self.name == 'all':
                srclist = SimFile.objects.all()
            else:
                assert False, ''
        else:
            srclist = self.simfiles

        return srclist.filter(tracking_status=TrackingStatus.Tracked)


class EnvironVar(models.Model):

    key = models.CharField(max_length=10000)
    value = models.CharField(max_length=10000, null=True)
    config = models.ForeignKey(RunConfiguration)


class SimRunStatus(object):

    Success = 'Success'
    UnhandledException = 'UnhandledException'
    TimeOut = 'Timeout'
    NonZeroExitCode = 'NonZeroExitCode'
    FileChanged = 'FileChanged'
    NeverBeenRun = 'NeverBeenRun'


class SimFileRun(models.Model):

    simfile = models.ForeignKey(SimFile)
    runconfig = models.ForeignKey(RunConfiguration)
    execution_date = models.DateTimeField('execution date')
    return_code = models.IntegerField()
    std_out = models.CharField(max_length=10000000)
    std_err = models.CharField(max_length=10000000)
    exception_type = models.CharField(max_length=10000,null=True, blank=False)
    exception_traceback = models.CharField(max_length=10000,null=True, blank=False)

    simulation_sha1hash = models.CharField(max_length=200)
    library_sha1hash = models.CharField(max_length=200)
    execution_time = models.IntegerField(null=True)

    def execution_data_string(self):
        import datetime
        exec_date = str(self.execution_date)
        d = datetime.datetime.strptime(exec_date,'%Y-%m-%d %H:%M:%S.%f')
        s = d.strftime('%Y-%m-%d %H:%M')
        return s

    def is_script_uptodate(self):
        res = str(self.simulation_sha1hash) == str(self.simfile.get_current_checksum())
        return res

    def get_status(self):
        if self.simulation_sha1hash != self.simfile.get_current_checksum():
            return SimRunStatus.FileChanged
        if self.execution_time is None:
            return SimRunStatus.TimeOut
        if self.exception_type:
            if 'TimeoutException' in self.exception_type:
                return SimRunStatus.TimeOut

            return SimRunStatus.UnhandledException
        if self.return_code != 0:
            return SimRunStatus.NonZeroExitCode
        return SimRunStatus.Success


class SimFileRunOutputImage(models.Model):

    original_name = models.CharField(max_length=10000)
    hash_name = models.CharField(max_length=10000)
    hash_thumbnailname = models.CharField(max_length=10000)
    simulation = models.ForeignKey(SimFileRun, related_name='output_images')

    def hash_name_short(self):
        return self.hash_name.split('/')[-1]

    def hash_thumbnailname_short(self):
        return self.hash_thumbnailname.split('/')[-1]



class SimQueueEntryState(models.Model):

    Waiting = 'Waiting'
    Executing = 'Executing'


class SimQueueEntry(models.Model):

    simfile = models.ForeignKey(SimFile)
    runconfig = models.ForeignKey(RunConfiguration)
    submit_time = models.DateTimeField('submission_time', default=datetime.datetime.now)
    simulation_start_time = models.DateTimeField(null=True, default=None)
    simulation_last_heartbeat = models.DateTimeField(null=True, default=None)
    status = models.CharField(max_length=1000, default=SimQueueEntryState.Waiting )


    @classmethod
    def create(cls, sim_file, runconfig):
        queue_entry = SimQueueEntry(simfile=sim_file,
                                    runconfig=runconfig)
        queue_entry.save()

    def get_simulation_time(self):
        return datetime.datetime.now() - self.simulation_start_time

    def time_since_last_heartbeat_in_s(self):
        if not self.simulation_last_heartbeat:
            return -1
        return (datetime.datetime.now()
                - self.simulation_last_heartbeat).total_seconds()

    def resubmit_if_process_died(self):
        if self.status == SimQueueEntryState.Executing:
            if self.time_since_last_heartbeat_in_s() > 60:
                print 'Resubmitting'
                self.status = SimQueueEntryState.Waiting
                self.save()

    @classmethod
    def trim_dangling_jobs(cls):
        for queue_entry in SimQueueEntry.objects.all():
            queue_entry.resubmit_if_process_died()


