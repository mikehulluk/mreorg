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


from django.conf.urls.defaults import *

from dajaxice.core import dajaxice_autodiscover
dajaxice_autodiscover()
from django.conf import settings


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()


p = (
    (r'^$', 'frontend.views.index'),

    (r'^simulationfileruns/(\d+)', 'frontend.views.simulationfilerun_details'),
    (r'^simulationfileruns/(\d+)', 'frontend.views.simulationfile_details'),
    (r'^viewpotentialsimulationfiles$', 'frontend.views.viewpotentialsimulationfiles'),
    (r'^viewsimulationqueue$', 'frontend.views.viewsimulationqueue'),

    # Untracked/tracked Simulations:
    (r'^do/update_potential_simulation_files', 'frontend.views.doupdatepotentialsimulationfiles'),
    (r'^do/potential_to_actual_simulation', 'frontend.views.dopotentialtoactualsimulationfiles'),
    (r'^do/actual_to_potential_simulation', 'frontend.views.doactualtopotentialsimulationfiles'),
    (r'^do/addpotentialsimulationlocation', 'frontend.views.doaddpotentialsimulationlocation'),
    (r'^do/track_all_simulation_files', 'frontend.views.dotrackallsimulationfiles'),


    (r'^do/queuesimulations', 'frontend.views.doqueuesimulations'),
    (r'^do/removesimulationsfromqueue', 'frontend.views.doremovesimulationsfromqueue'),
    (r'^do/editsimulationfile/(\d+)', 'frontend.views.doeditsimulationfile'),

    (r'^simulationfiles/(\d+)$', 'frontend.views.simulationfile_details'),



    (r'^viewsimulationoutputsummaries', 'frontend.views.view_simulation_output_summaries'),

    (r'^viewsimulationfailures$', 'frontend.views.view_simulation_failures'),
    
    # Image request
    (r'^image/([\w.]*)$', 'frontend.views.get_image_file'),

    # Ajax requests:
    (r'^%s/' % settings.DAJAXICE_MEDIA_PREFIX, include('dajaxice.urls')),
)


root_dir = '/home/michael/hw_to_come/libs/mreorg/src/mreorg/curator/'

p = p + (
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': root_dir+'/static/'}),
    (r'^site_media/javascript/(?P<path>.*)$', 'django.views.static.serve', {'document_root': root_dir +'/static/javascript/'}),
    )


p = p+ ( 
        (r'^simimages/(?P<path>.*)$', 'django.views.static.serve', {'document_root': root_dir + '/frontend/data/images/'}),
        )


urlpatterns = patterns('', *p)
