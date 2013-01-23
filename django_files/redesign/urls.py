from django.conf.urls import patterns, url

from redesign import views

urlpatterns = patterns('',
    url(r'^$/', views.index, name='index')
)