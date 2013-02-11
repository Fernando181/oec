# Create your views here.
# Django
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse, Http404, HttpResponsePermanentRedirect, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
from django.core.urlresolvers import resolve
from django.conf import settings
from django.http import HttpResponse
from usa.models import *
from redesign.helpers import get_app_name
from usa.helpers import *

def index(request):
  output = "Usa say Hello World!"
  return HttpResponse(output)

def build(request,app_name,trade_flow,origin,destination,industry,classification,value="pay",year=2008):
  
  # make sure app name is in the list of possiblities
  app_name = get_app_name(app_name) or "tree_map"
  
  # There is no tradeflow in US data. Default to export, all
  trade_flow = "export"
  destination = "all"
  
  # Check whether country can be found in database. I
  origin = get_county(origin,classification) or origin
  
  # format of the app. Can only be CASY or SAPY    
  app_type = get_app_type(origin,destination,industry,year)
  
  # Get Naics industry.
  industry = get_industry(industry) or industry
  
  output = """
  This would be a %s, %s app.<br>
  Source: %s <br>
  Destination: %s <br>
  Industry: %s <br>
  Type: %s
  """ % (app_name, app_type, origin, destination, industry, value)
  
  return HttpResponse(output)
  
def county(request):
  allof = County.objects.all()
  output = ', <br>'.join([c.name for c in allof])
  return HttpResponse(output)
  
def state(request):
  allof = State.objects.all()
  output = ', <br>'.join([c.name for c in allof])
  return HttpResponse(output)  

def naics(request):
  allof = Naics.objects.all()
  output = ', <br>'.join([c.name for c in allof])
  return HttpResponse(output)
  
  
  
    
  

    