# Create your views here.
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponse
from redesign.models import *
from redesign.helpers import *
import math
import json

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
  years_available = get_years(classification)
  
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
  
  # assemble the uri
  api_uri = "/api/%s/%s/%s/%s/%s/%s" % (classification, trade_flow, origin, destination, product, year)
  
  # Return page without visualization data
  return render_to_response("explore/index.html", {
     "question": question,
     "trade_flow": trade_flow,
     "origin": origin,
     "destination": destination,
     "classification": classification,
     "product": product,
     "year": year,
     "years_available": years_available["all"],
     "app_name": app_name,
     "app_type": app_type
    }, context_instance=RequestContext(request))


def api_casy(request, classification, trade_flow, origin, year):
  
  lang = "en"
  #######
  #  Sanity Checks
  
  ## Country
  origin = get_country(origin)
  if origin is None:
    raise Exception("Country Does not Exist.")
  
  ## Year
  if int(year) not in get_years(classification):
    raise Exception("%s dataset does not support the year %s."% (classification, year))
  
  ## Clasification & Django Data Call
  if classification == "sitc4":
    raw = Sitc4_cpy.objects.filter(country=origin.id).filter(year=year)
  elif classification == "hs4":
    raw = Hs4_cpy.objects.filter(country=origin.id).filter(year=year)
  else:
    raise Exception("Dataset not supported.")
    
  ## Trade Flow - defaults to "import" if fail 
  #### Net Export
  if trade_flow == "net_export":
    exclude = []
    for r in raw: 
      if (r.export_value - r.import_value) <= 0: exclude.append(r.pk)       
    exp = raw.exclude(pk__in=exclude) 
    for e in exp: e.net_export =  e.export_value - e.import_value
    total_val = sum([prod.net_export for prod in exp])
    
    build = [{"year":e.year,"item_id":e.product.id,"abbr":e.product.code,
              "name":e.product.name_en, "value":e.net_export,"rca":e.export_rca,
              "share":(e.net_export / total_val) * 100} for e in exp]
  ####  Net Import
  elif trade_flow == "net_import":
    exclude = []
    for r in raw: 
      if (r.import_value - r.export_value) <= 0: exclude.append(r.pk)
    exp = raw.exclude(pk__in=exclude)  
    for e in exp: e.net_import = e.import_value - e.export_value
    total_val = sum([prod.net_import for prod in exp])
    
    build = [{"year":e.year,"item_id":e.product.id,"abbr":e.product.code,
              "name":e.product.name_en, "value":e.net_import,"rca":e.export_rca,
              "share":(e.net_import / total_val) * 100} for e in exp]
  ####  Export
  elif trade_flow == "export":
    exp = raw.filter(export_value__gt=0)
    total_val = sum([prod.export_value for prod in exp])
    
    build = [{"year":e.year,"item_id":e.product.id,"abbr":e.product.code,
              "name":e.product.name_en, "value":e.export_value,"rca":e.export_rca,
              "share":(e.export_value / total_val) * 100 } for e in exp]
  #### Import
  else:
  
    exp = raw.filter(import_value__gt=0)
    total_val = sum([prod.import_value for prod in exp])
    
    build = [{"year":e.year,"item_id":e.product.id,"abbr":e.product.code,
              "name":e.product.name_en, "value":e.import_value,"rca":e.export_rca,
              "share":(e.import_value / total_val) * 100 } for e in exp]
  
  # Define parameters for query
  year_where = "AND year = %s" % (year,)
  rca_col = "null"
  if trade_flow == "net_export":
    val_col = "export_value - import_value as val"
    rca_col = "export_rca"
  elif trade_flow == "net_import":
    val_col = "import_value - export_value as val"
  elif trade_flow == "export":
    val_col = "export_value as val"
    rca_col = "export_rca"
  else:
    val_col = "import_value as val"
    
  ## This execution still calls out a direct query to the DB.
  ## Why can't this be done with Django's object model? Grr confused

  # Create query [year, id, abbrv, name_lang, val, export_rca]
  
  q = """
    SELECT year, p.id, p.code, p.name_%s, %s, %s 
    FROM observatory_%s_cpy as cpy, observatory_%s as p 
    WHERE country_id=%s and cpy.product_id = p.id %s
    HAVING val > 0
    ORDER BY val DESC
    """ % (lang, val_col, rca_col, classification, classification, origin.id, year_where)
  
  # rows = raw_q(query=q, params=None)
  # total_val = sum([r[4] for r in rows])
  # # Add percentage value to return vals
  # # rows = [list(r) + [(r[4] / total_val)*100] for r in rows]
  # rows = [{"year":r[0], "item_id":r[1], "abbrv":r[2], "name":r[3], "value":r[4], "rca":r[5], 
  #               "share": (r[4] / total_val)*100} for r in rows]
  # 
  
 
  
  # Prepare JSON response
  json_response = {}
  json_response["data"] = build
  json_response["attr_data"] = Sitc4.objects.get_all(lang) if classification == "sitc4" else Hs4.objects.get_all(lang)
  json_response["origin"] = origin.to_json()
  json_response["class"] =  classification
  json_response["title"] = "What does %s %s?" % (origin.name, trade_flow.replace("_", " "))
  json_response["year"] = year
  json_response["item_type"] = "product"
  json_response["total_val"] = total_val
  #json_response["other"] = query_params
  
  # Return to browser as JSON for AJAX request
  return HttpResponse(json.dumps(json_response))   
    
  
def api_sapy(request, classification, trade_flow, product, year):
  lang = "en"
  product = get_product(product, classifcation)
  
  
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
  
  