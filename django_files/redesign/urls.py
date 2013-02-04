from django.conf.urls import patterns, url

from redesign import views

urlpatterns = patterns('',
    (r'^$', 'redesign.views.index'),
    # Overview 
    (r'^country/(?P<country>\w{2,3})/','redesign.views.country'),
    
    # HS4 CLASS
    (r'^build/hs4/(?P<app_name>[a-z_]+)/(?P<trade_flow>\w{6,10})/(?P<country1>\w{3,4})/(?P<country2>\w{3,4})/(?P<product>\w{3,4})/(?P<year>[0-9\.]+)/$', 'redesign.views.build', {'classification':'hs4'}),
    (r'^build/hs4/(?P<app_name>[a-z_]+)/(?P<trade_flow>\w{6,10})/(?P<country1>\w{3,4})/(?P<country2>\w{3,4})/(?P<product>\w{3,4})/$', 'redesign.views.build', {'classification':'hs4'}),  
    # SITC4 CLASS
    (r'^build/sitc4/(?P<app_name>[a-z_]+)/(?P<trade_flow>\w{6,10})/(?P<country1>\w{3,4})/(?P<country2>\w{3,4})/(?P<product>\w{3,4})/(?P<year>[0-9\.]+)/$', 'redesign.views.build', {'classification':'sitc4'}),
    (r'^build/sitc4/(?P<app_name>[a-z_]+)/(?P<trade_flow>\w{6,10})/(?P<country1>\w{3,4})/(?P<country2>\w{3,4})/(?P<product>\w{3,4})/$', 'redesign.views.build', {'classification':'sitc4'}),
    
    #  Instances of US data buids
    # MSA CLASS
    (r'^build/msa/(?P<app_name>[a-z_]+)/(?P<trade_flow>\w{6,10})/(?P<source>\d{5})/(?P<destination>\w{3,4})/(?P<industry>\w{3,4})/(?P<value>\w{3})/(?P<year>[0-9\.]+)/$', 'usa.views.build', {'classification':'msa'}),
    (r'^build/msa/(?P<app_name>[a-z_]+)/(?P<trade_flow>\w{6,10})/(?P<source>\d{5})/(?P<destination>\w{3,4})/(?P<industry>\w{3,4})/(?P<value>\w{3})/$', 'usa.views.build', {'classification':'msa'}),
    (r'^build/msa/(?P<app_name>[a-z_]+)/(?P<trade_flow>\w{6,10})/(?P<source>\d{5})/(?P<destination>\w{3,4})/(?P<industry>\w{3,4})/$', 'usa.views.build', {'classification':'msa'}),
  
    # County Class
    (r'^build/county/(?P<app_name>[a-z_]+)/(?P<trade_flow>\w{6,10})/(?P<source>\d{5})/(?P<destination>\w{3,4})/(?P<industry>\w{3,4})/(?P<value>\w{3})/(?P<year>[0-9\.]+)/$', 'usa.views.build', {'classification':'msa'}),
    (r'^build/county/(?P<app_name>[a-z_]+)/(?P<trade_flow>\w{6,10})/(?P<source>\d{5})/(?P<destination>\w{3,4})/(?P<industry>\w{3,4})/(?P<value>\w{3})/$', 'usa.views.build', {'classification':'msa'}),
    (r'^build/county/(?P<app_name>[a-z_]+)/(?P<trade_flow>\w{6,10})/(?P<source>\d{5})/(?P<destination>\w{3,4})/(?P<industry>\w{3,4})/$', 'usa.views.build', {'classification':'msa'}),
    
    # BLOG ##################################################################
    (r'^blog/$', "blog.views.blog_index")
    
    # ATLAS ##################################################################
    
    # ABOUT ##################################################################
    
    
    
    
)