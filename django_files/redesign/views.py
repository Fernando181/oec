# Create your views here.
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponse
from observatory.models import *
from redesign.helpers import *
import math

def index(request):
  output = "Redesign Index"
  return HttpResponse(output)
  
def country(request, country):
  # Find out what country the user is asking for
  try:
    c = Country.objects.get(name_3char=country)
  except Country.DoesNotExist:
    try:
      c = Country.objects.get(name_2char=country)
    except Country.DoesNotExist:
      return HttpResponse("Is that a new country? Never heard of it.")  
  return HttpResponse(c)  

def build(request,app_name,trade_flow,country1,country2,product,classification,year=2008):
  
  # get distinct years for the given dataset
  years = get_years(classification)
  
  output = "Redesign says Hello World!"
  return HttpResponse(output)


# Returns the Country object or None
def get_country(country):
  # first try looking up based on 3 character code
  try:
    c = Country.objects.get(name_3char=country)
  except Country.DoesNotExist:
    # next try 2 character code
    try:
      c = Country.objects.get(name_2char=country)
    except Country.DoesNotExist:
      c = None
  return c

# Returns the Product object or None
def get_product(product, prod_class):
  # first try looking up based on 3 character code
  if prod_class == "hs4":
    try:
      p = Hs4.objects.get(code=product)
    except Hs4.DoesNotExist:
      # next try SITC4
      try:
        conv_code = Sitc4.objects.get(code=product).conversion_code
        p = Hs4.objects.get(code=conv_code)
      except Hs4.DoesNotExist:
        p = None
  else:
    try:
      p = Sitc4.objects.get(code=product)
    except Sitc4.DoesNotExist:
      # next try SITC4
      try:
        conv_code = Hs4.objects.get(code=product).conversion_code
        p = Sitc4.objects.get(code=conv_code)
      except Hs4.DoesNotExist:
        p = None
  return p

# Returns app type in CCPY format  
def get_app_type(country1, country2, product, year):
  # country / all / show / year
  if country2 == "all" and product == "show":
    return "casy"
  
  # country / show / all / year
  elif country2 == "show" and product == "all":
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
    
def predict(request, country):
  c = get_country(country)
  
  ### Present
  cepiis_present_list = Hs4_Cepii.objects.filter(iso=country,present=1)
  #cepiis_present = ['{percent:.2%}'.format(percent=float(elem.m_resid)) for elem in cepiis_present_list]
  
  remain_present = []
  disappear = []
  for item in cepiis_present_list:
    if math.fabs(item.m_resid) >= 0.5:
      disappear.append(item)
    else:
      remain_present.append(item)
  
  ### Absent
  cepiis_absent_list = Hs4_Cepii.objects.filter(iso=country,absent=1)
  appear = []
  remain_absent = []
  for item in cepiis_absent_list:
    if math.fabs(item.m_resid) >= 0.5:
      appear.append(item)
    else:
      remain_absent.append(item)  
      
      
  return render_to_response("redesign/predict.html",{'country':c, 'cepii_present':cepiis_present_list,'cepii_absent':cepiis_absent_list,'disappear':disappear,'remain_present':remain_present, 'appear':appear, 'remain_absent':remain_absent}, context_instance=RequestContext(request))    