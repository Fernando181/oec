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

def build(request, app_name, trade_flow, origin, destination, product, classification, year=2010):
  
  # make sure app name is in the list of possiblities
  app_name = get_app_name(app_name) or "tree_map"
  
  # make sure trade flow is in the list of possiblities
  trade_flow = get_trade_flow(trade_flow) or "export"
  
  # get distinct years for the given dataset
  years = get_years(classification)
  
  # get the format of the app
  app_type = get_app_type(origin, destination, product, year)
   
  # get our countries from the db
  origin = get_country(origin) or origin
  destination = get_country(destination) or destination
  
  # get our product name from the db
  product = get_product(product, classification) or product
  
  # get the question for the data requested by the URL
  question = get_question(app_type, origin=origin, trade_flow=trade_flow, 
                            product=product, destination=destination)
  
  # Return page without visualization data
  return render_to_response("explore/index.html", {
     "question": question,
     "trade_flow": trade_flow,
     "origin": origin,
     "destination": destination,
     "classification": classification,
     "product": product,
     "year": year,
     "years": years,
     "app_name": app_name,
     "app_type": app_type
    }, context_instance=RequestContext(request))

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