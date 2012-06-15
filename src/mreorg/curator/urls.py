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

from django.conf import settings
from django.conf.urls.defaults import include, patterns

from dajaxice.core import dajaxice_autodiscover
dajaxice_autodiscover()




p = (
    (r'^$', 'mreorg.curator.frontend.views.index'),

    (r'^simulationfileruns/(\d+)', 'mreorg.curator.frontend.views.simulationfilerun_details'),
    (r'^simulationfileruns/(\d+)', 'mreorg.curator.frontend.views.simulationfile_details'),
    (r'^viewpotentialsimulationfiles$', 'mreorg.curator.frontend.views.viewpotentialsimulationfiles'),
    (r'^viewsimulationqueue$', 'mreorg.curator.frontend.views.viewsimulationqueue'),

    # Untracked/tracked Sims:
    (r'^do/update_potential_simulation_files', 'mreorg.curator.frontend.views.doupdatepotentialsimulationfiles'),
    (r'^do/potential_to_actual_simulation', 'mreorg.curator.frontend.views.dopotentialtoactualsimulationfiles'),
    (r'^do/actual_to_potential_simulation', 'mreorg.curator.frontend.views.doactualtopotentialsimulationfiles'),
    (r'^do/addpotentialsimulationlocation', 'mreorg.curator.frontend.views.doaddpotentialsimulationlocation'),
    (r'^do/track_all_simulation_files', 'mreorg.curator.frontend.views.dotrackallsimulationfiles'),


    (r'^do/queuesimulations', 'mreorg.curator.frontend.views.doqueuesimulations'),
    (r'^do/removesimulationsfromqueue', 'mreorg.curator.frontend.views.doremovesimulationsfromqueue'),
    (r'^do/editsimulationfile/(\d+)', 'mreorg.curator.frontend.views.doeditsimulationfile'),

    (r'^simulationfiles/(\d+)$', 'mreorg.curator.frontend.views.simulationfile_details'),



    (r'^viewsimulationoutputsummaries', 'mreorg.curator.frontend.views.view_simulation_output_summaries'),

    (r'^viewsimulationfailures$', 'mreorg.curator.frontend.views.view_simulation_failures'),

    # Image request
    (r'^image/([\w.]*)$', 'mreorg.curator.frontend.views.get_image_file'),

    # Ajax requests:
    (r'^%s/' % settings.DAJAXICE_MEDIA_PREFIX, include('dajaxice.urls')),
)


this_dir = os.path.dirname(__file__)


p = p + (
    # Static files:
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.join(this_dir,'static/')}),
    (r'^site_media/javascript/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.join(this_dir, 'static/javascript/')}),
    )


urlpatterns = patterns('', *p)
