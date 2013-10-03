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

from django.conf import settings
from django.conf.urls.defaults import include, patterns
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from dajaxice.core import dajaxice_autodiscover
dajaxice_autodiscover()

views_mod = 'mreorg.curator.frontend.views'
url_patterns = (
    (r'^$', 'mreorg.curator.frontend.views.view_overview'),


    # Main pages:
    (r'^overview$', views_mod + '.view_overview'),
    (r'^tracking$', views_mod + '.view_tracking'),
    (r'^viewsimulationoutputsummaries', views_mod + '.view_sim_output_summaries'),
    (r'^viewsimulationfailures$', views_mod+ '.view_simulation_failures'),
    (r'^viewsimulationqueue$', views_mod + '.viewsimulationqueue'),
    (r'^viewconfigurations$', views_mod + '.view_configurations'),

    # Details about specific files and runs:
    (r'^simfiles/(\d+)$', views_mod + '.simfile_details'),
    (r'^simfileruns/(\d+)', views_mod + '.simfilerun_details'),
    (r'^simfile/(\d+)', views_mod + '.simfile_details'),

    # Tracking
    (r'^do/track/rescan', views_mod + '.do_track_rescanfs'),
    (r'^do/track/track_sim', views_mod + '.do_track_sim'),
    (r'^do/track/untrack_sim', views_mod + '.do_untrack_sim'),
    (r'^do/track/untrack_src_dir/(\d+)', views_mod + '.do_untrack_src_dir'),
    (r'^do/track/add_src_dir', views_mod + '.do_track_src_dir'),
    (r'^do/track/track_all_sims', views_mod + '.do_track_all'),
    (r'^do/track/untrack_all_sims', views_mod + '.do_untrack_all'),

    # Queuing:
    (r'^do/queue/add_sims', views_mod + '.do_queue_add_sims'),
    (r'^do/editsimfile/(\d+)', views_mod + '.doeditsimfile'),


    # Handle image request
    (r'^image/([\w.]*)$', 'mreorg.curator.frontend.views.get_image_file'),

    # Handle Ajax requests:
    (r'^%s/' % settings.DAJAXICE_MEDIA_PREFIX, include('dajaxice.urls')),
)


urlpatterns = patterns('', *url_patterns) + staticfiles_urlpatterns()
