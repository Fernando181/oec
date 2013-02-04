from django.conf.urls import patterns, url

from usa import views

urlpatterns = patterns('',
    (r'^', 'usa.views.index'),
    (r'^msa', 'usa.views.msa'),
    (r'^county', 'usa.views.county'), 
    (r'^state', 'usa.views.state'),
    (r'^naics', 'usa.views.naics')
)