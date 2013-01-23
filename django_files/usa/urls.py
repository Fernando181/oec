from django.conf.urls import patterns, url

from usa import views

urlpatterns = patterns('',
    url(r'^$/', views.index, name='index')
)