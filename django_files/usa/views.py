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

def index(request):
  output = "Usa say Hello World!"
  return HttpResponse(output)

def build(request,app_name,trade_flow,source,destination,industry,classification,value="pay",year=2008):
  
  
  # Thinking. At this stage the actual visualization can only have 
  # trade_flow of export and country2 of 'all' (regardless of msa or county)
  app_type = get_app_type(source,destination,industry,year)
  
  # Check whether country can be found in database
  if classification == 'msa':
    try:
      source = Msa.objects.get(code=source)
    except Country.DoesNotExist:
      source = "Not support MSA"
  
  if classification == 'county':
    try:
      source = Msa.objects.get(fips=source)
    except Country.DoesNotExist:
      source = "Not support county"
  
  
  # msa = [None, None]
  # country_lists = [None, None]
  # for i, country in enumerate([country1, country2]):
  #   if country != "show" and country != "all":
  #     try:
  #       msas[i] = Msa.objects.get(name_3char=country)
  #     except Country.DoesNotExist:
  #       countries[i] = "Not support MSA"
  #       #alert = {"title": "Country could not be found",
  #       # "text": "There was no country with the 3 letter abbreviateion <strong>%s</strong>. Please double check the <a href='/about/data/country/'>list of countries</a>."%(country)}
  
  # Industry check
  
  if industry != "show" and industry != "all":
    try:
      naics = Naics.objects.get(naics6=industry)
    except Naics.DoesNotExist:
      naics = "Industry not listed"
  else:
    naics = None
  
  
  output = """
  This would be a %s app.<br>
  Source: %s <br>
  Destination: %s <br>
  Industry: %s <br>
  Type: %s
  """ % (classification, source, destination, naics, value)
  
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
  
def get_app_type(source, destination, industry, year):
  # location / all / show / year
  if destination == "all" and product == "show":
    return "casy"
  
  # show / all / industry / year
  elif source == "show" and product == "all":
    return "csay"
  
  # show / all / product / year
  elif country1 == "show" and country2 == "all":
    return "sapy"
  
  # country / country / show / year
  elif product == "show":
    return "ccsy"
  
  #  country / show / product / year
  else:
    return "cspy"
  
  
    
  

    