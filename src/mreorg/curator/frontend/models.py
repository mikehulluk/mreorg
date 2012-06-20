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
import os
import datetime
import StringIO

from django.db import models
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

import mreorg
from django.db import transaction





class Options(object):
    MinimumFileCheckInterval = datetime.timedelta(minutes=5)









class SourceSimDir(models.Model):
    class Meta():
        ordering = ['directory_name']

    directory_name = models.CharField(max_length=1000)
    should_recurse = models.BooleanField()

    def does_exist(self):
        return os.path.exists( self.directory_name)

    @classmethod
    def create(cls, directory_name, should_recurse=True):
        if SourceSimDir.objects.filter(directory_name = directory_name).count() !=0:
            return

        # Create and save
        p = SourceSimDir(directory_name=directory_name, should_recurse=should_recurse)
        p.save()



class TrackingStatus(object):
    Tracked='Tracked'
    NotTracked='Nottracked'












class SimFile(models.Model):
    class Meta():
        ordering = ['full_filename']
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
    last_run = models.ForeignKey('SimFileRun',null=True, related_name='+')

    @classmethod
    def get_tracked_sims(cls, **kwargs):
        if kwargs:
            return SimFile.objects.get(tracking_status=TrackingStatus.Tracked, **kwargs)
        return SimFile.objects.filter(tracking_status=TrackingStatus.Tracked)

    @classmethod
    def get_untracked_sims(cls,**kwargs):
        if kwargs:
            return SimFile.objects.get(tracking_status=TrackingStatus.NotTracked, **kwargs)
        #return SimFile.objects.all()
        return SimFile.objects.filter(tracking_status=TrackingStatus.NotTracked)

    @classmethod
    def create(cls, full_filename, tracked):
        if tracked:
            simfile = SimFile(full_filename = full_filename, tracking_status = TrackingStatus.Tracked)
        else:
            simfile = SimFile(full_filename = full_filename, tracking_status = TrackingStatus.NotTracked)
        simfile.save()
        return simfile




    @classmethod
    @transaction.commit_on_success
    def update_all_db(cls, directory):
        excludes = ('py.py','__init__.py' )

        def accept_file( filename ):
            if not filename.endswith('.py'):
                return False
            if filename.startswith("__"):
                return False

            dirname, fname = os.path.split(filename)
            if fname in excludes:
                return False
            return True

        def handlefile(filename):
            print 'Checking: ', filename
            try:
                SimFile.objects.get(full_filename=filename)
            except:
                SimFile.create(full_filename = filename, tracked=False)


        print 'Updating untracked simulation files', directory
        for (dirpath, dirnames, filenames) in os.walk( directory ):
            for filename in filenames:
                if accept_file(filename):
                    handlefile( os.path.join( dirpath, filename ) )








    # Handle Caching:
    # ##########################################
    def _is_cache_valid(self):
        if not self.last_read_time:
            return False
        # We only maximally recalculate the hash every so often:
        if self.last_read_sha1 - datetime.datetime.now() < Options.MinimumFileCheckInterval:
            return True
        if self.get_current_checksum() == self.last_read_sha1:
            return True
        return False

    def recache_from_filesystem(self):
        with open(self.full_filename) as f:
            code = f.read()

        self.last_read_sha1 = self.get_current_checksum()
        self.last_read_time = datetime.datetime.now()
        self.last_read_contents  = code
        self.last_read_docstring = mreorg.utils.extract_docstring_from_fileobj(StringIO.StringIO( code ) )
        self.last_read_htmlcode = highlight(code, PythonLexer(), HtmlFormatter())

        runs = self.get_runs()
        self.last_run = runs[0] if runs else None
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

    def get_latest_run(self):
        return self.last_run

    def get_current_checksum(self):
        return mreorg.get_file_sha1hash(self.full_filename)

    def get_short_filename(self):
        return os.path.split(self.full_filename)[1]

    def get_runs(self):
        return SimFileRun.objects. \
                    filter(simfile=self.id). \
                    order_by('-execution_date')


    def get_status(self):
        last_run = self.get_latest_run()
        if not last_run:
            return SimRunStatus.NeverBeenRun
        else:
            return last_run.get_status()

    def get_last_executiontime(self):
        last_run = self.get_latest_run()
        if not last_run:
            return 'Unknown'
        else:
            return last_run.execution_time

    def is_queued(self):
        return self.simqueueentry_set.count() != 0

    def getCSSQueueState(self):
        p = self.is_queued()
        LUT = { True:'SimQueued',False:'SimNotQueued'}
        return LUT[p]

#class UntrackedSimFile(SimFile):
#    pass
#class TrackedSimFile(SimFile):
#    pass






class SimRunStatus(object):
    Sucess = 'Sucess'
    UnhandledException = 'UnhandledException'
    TimeOut = 'Timeout'
    NonZeroExitCode = 'NonZeroExitCode'
    FileChanged = 'FileChanged'
    NeverBeenRun = 'NeverBeenRun'


class SimFileRun(models.Model):
    simfile = models.ForeignKey(SimFile)
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
        print exec_date
        #2012-01-02 14:28:29.129076
        d = datetime.datetime.strptime(exec_date,'%Y-%m-%d %H:%M:%S.%f')
        print d
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
        return SimRunStatus.Sucess

class SimFileRunOutputImage(models.Model):
    original_name = models.CharField(max_length=10000)
    hash_name = models.CharField(max_length=10000)
    hash_thumbnailname = models.CharField(max_length=10000)
    simulation = models.ForeignKey(SimFileRun, related_name='output_images')

    def hash_name_short(self):
        return self.hash_name.split("/")[-1]
    def hash_thumbnailname_short(self):
        return self.hash_thumbnailname.split("/")[-1]



class SimQueueEntryState(models.Model):
    Waiting = 'Waiting'
    Executing = 'Executing'

class SimQueueEntry(models.Model):
    simfile = models.ForeignKey(SimFile)
    submit_time = models.DateTimeField('submission_time', default=datetime.datetime.now)
    simulation_start_time = models.DateTimeField(null=True, default=None)
    status = models.CharField(max_length=1000, default=SimQueueEntryState.Waiting )

    @classmethod
    def create(cls, sim_file):
        queue_entry = SimQueueEntry( simfile = sim_file )
        queue_entry.save()



    def get_simulation_time(self):
        return datetime.datetime.now() - self.simulation_start_time
