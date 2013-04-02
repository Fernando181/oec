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
  # import time
#   start = time.time()
  #raise Exception ("Did we get to this API?")
  lang = "en"
  total_val={}
  #  Sanity Checks
  
  ## Country
  origin = get_country(origin)
  if origin is None:
    raise Exception("Country Does not Exist.")
  
  ## Year
  years_available = sorted(get_years(classification))
  
  # Magic numbers for per-capita figures
  magic = list(Country_Cy.objects.filter(country=origin.id).values('year','magic'))
                                #,year__range=(years_available[0],
                                #             years_available[-1])).values('year',
                                #                                          'magic')
  m = {}
  for i in magic: m[i['year']] = i['magic']
  
  ## Clasification & Django Data Call
  if classification == "sitc4":
    raw = Sitc4_cpy.objects.filter(country=origin.id)
  elif classification == "hs4":
    raw = Hs4_cpy.objects.filter(country=origin.id)
  else:
    raise Exception("Dataset not supported.")
    
  ## Trade Flow - defaults to "import" if fail 
  
  #### Net Export
  if trade_flow == "net_export":
    fast = list(raw.values('year',
                           'product',
                           'product__code',
                           'product__name_en',
                           'export_value',
                           'import_value',
                           'export_rca'
                           ))
    # Remove invalid
    fast = [x for x in fast if x['export_value'] - x['import_value'] > 0]
     # Add net index for convenince  
    for x in fast: 
      x['net'] = x['export_value'] - x['import_value']
    
    build = [{"year":e['year'],"item_id":e['product'],"abbr":e['product__code'],
              "name":e['product__name_en'], "value":e['net'],"rca":e['export_rca']} for e in fast]
  
  ####  Net Import
  elif trade_flow == "net_import":
    fast = list(raw.values('year','product','product__code','product__name_en',
                  'export_value','import_value','export_rca'))
    # Remove invalid
    fast = [x for x in fast if x['import_value'] - x['export_value'] > 0]
     # Add net index for convenince  
    for x in fast: 
      x['net'] = x['import_value'] - x['export_value']
    
    build = [{"year":e['year'],"item_id":e['product'],"abbr":e['product__code'],
              "name":e['product__name_en'], "value":e['net'],"rca":e['export_rca']} for e in fast]
    
  ####  Export
  elif trade_flow == "export":
    exp = raw.filter(export_value__gt=0)
    
    fast = raw.values('year','product','product__code','product__name_en',
                      'export_value','export_rca')
         
    build = [{"year":e['year'],"item_id":e['product'],"abbr":e['product__code'],
              "name":e['product__name_en'], "value":e['export_value'],"rca":e['export_rca']} for e in fast]
            
  #### Import
  else: 
    exp = raw.filter(import_value__gt=0)
    fast = exp.values('year','product','product__code','product__name_en',
                      'import_value','export_rca')

    build = [{"year":e['year'],"item_id":e['product'],"abbr":e['product__code'],
              "name":e['product__name_en'], "value":e['import_value'],"rca":e['export_rca']} for e in fast]    
  
  # Set query params with our changes
  query_params = request.GET.copy()
  query_params["lang"] = lang
  query_params["product_classification"] = classification
  # Prepare JSON response
  json_response = {}
  json_response["data"] = build
  json_response["attr_data"] = Sitc4.objects.get_all(lang) if classification == "sitc4" else Hs4.objects.get_all(lang)
  json_response["origin"] = origin.to_json()
  json_response["class"] =  classification
  json_response["title"] = get_question("casy", trade_flow=trade_flow,origin=origin)
  #"What does %s %s?" % (origin.name, trade_flow.replace("_", " "))
  json_response["year"] = year
  json_response["magic"] = m
  json_response["item_type"] = "product"
  json_response["app_type"] = "casy"
  json_response["other"] = query_params
  
  # raise Exception(time.time() - start)
  # Return to browser as JSON for AJAX request
  return HttpResponse(json.dumps(json_response))   
      
def api_sapy(request, classification, trade_flow, product, year):
  lang = "en"
  total_val = {}
  #  Sanity Checks
  
  ## Product
  product = get_product(product,classification)
  if product is None:
    raise Exception("Product Does not Exist.")
  
  ## Year
  years_available = get_years(classification)

  ## Clasification & Django Data Call
  if classification == "sitc4":
    raw = Sitc4_cpy.objects.filter(product=product.id)
  elif classification == "hs4":
    raw = Hs4_cpy.objects.filter(product=product.id)
  else:
    raise Exception("Dataset not supported.")
   
  ## Trade Flow - defaults to "import" if fail 
  #### Net Export
  if trade_flow == "net_export":
    
    fast = list(raw.values('year','country','country__name_3char','country__name_en',
                  'export_value','import_value','export_rca'))
    # Remove invalid
    fast = [x for x in fast if x['export_value'] - x['import_value'] > 0]
     # Add net index for convenince  
    for x in fast: 
      x['net'] = x['export_value'] - x['import_value']
    
    build = [{"year":e['year'],"item_id":e['country'],"abbr":e['country__name_3char'],
              "name":e['country__name_en'], "value":e['net'],"rca":e['export_rca']} for e in fast]
   
  ####  Net Import
  elif trade_flow == "net_import":
    fast = list(raw.values('year','country','country__name_3char','country__name_en',
                  'export_value','import_value','export_rca'))
    # Remove invalid
    fast = [x for x in fast if x['import_value'] - x['export_value'] > 0]
     # Add net index for convenince  
    for x in fast: 
      x['net'] = x['import_value'] - x['export_value']
    
    build = [{"year":e['year'],"item_id":e['country'],"abbr":e['country__name_3char'],
              "name":e['country__name_en'], "value":e['net'],"rca":e['export_rca']} for e in fast]
   
  ####  Export
  elif trade_flow == "export":
    exp = raw.filter(export_value__gt=0)
    
    fast = exp.values('year','country','country__name_3char','country__name_en',
                      'export_value','export_rca')
    
    build = [{"year":e['year'],"item_id":e['country'],"abbr":e['country__name_3char'],
              "name":e['country__name_en'], "value":e['export_value'],"rca":e['export_rca']} for e in fast]  
    
  #### Import
  else:
  
    exp = raw.filter(import_value__gt=0)
    fast = exp.values('year','country','country__name_3char','country__name_en',
                      'import_value','export_rca')
    
    build = [{"year":e['year'],"item_id":e['country'],"abbr":e['country__name_3char'],
              "name":e['country__name_en'], "value":e['import_value'],"rca":e['export_rca']} for e in fast]
    
  # Set query params with our changes
  query_params = request.GET.copy()
  query_params["lang"] = lang
  query_params["product_classification"] = classification
  ## Build JSON object ##
  json_response = {}
  json_response["data"] = build            
  json_response["attr_data"] = Country.objects.get_all(lang)
  json_response["product"] = product.to_json()
  json_response["title"] = get_question("sapy", trade_flow=trade_flow,product=product)#"Who %ss %s?" % (trade_flow.replace("_", " "), product.name_en)
  json_response["class"] =  classification
  json_response["year"] = year
  json_response["item_type"] = "country"
  json_response["app_type"] = "sapy"
  json_response["other"] = query_params   
  
  # Return to browser as JSON for AJAX request
  return HttpResponse(json.dumps(json_response))         
  
def api_csay(request, classification, trade_flow, origin, year):
  lang = "en"
  #  Sanity Checks
  
  ## Country
  origin = get_country(origin)
  if origin is None:
    raise Exception("Country Does not Exist.")
  
  ## Year
  years_available = get_years(classification)
  
  ## Clasification & Django Data Call
  if classification == "sitc4":
    raw = Sitc4_ccpy.objects.filter(origin=origin.id)
  elif classification == "hs4":
    raw = Hs4_ccpy.objects.filter(origin=origin.id)
  else:
    raise Exception("Dataset not supported.")   
  
  ## Trade Flow - defaults to "import" if fail 
  #### Net Export
  if trade_flow == "net_export":
    fast = list(raw.values('destination','year',
                           'destination__name_en',
                           'destination__name_3char').annotate(imp=Sum('import_value'),exp=Sum('export_value')))
                           
    fast = [x for x in fast if x['exp'] - x['imp'] > 0]
    # For convenience
    for x in fast: x['net'] = x['exp'] - x['imp']                        
    
    build = [{"year":e['year'],"item_id":e['destination'], "name":e['destination__name_en'], 
              "abbr":e['destination__name_3char'], "value":e['net']} for e in fast]
                           
  elif trade_flow == "net_import":
    fast = list(raw.values('destination','year',
                           'destination__name_en',
                           'destination__name_3char').annotate(imp=Sum('import_value'),exp=Sum('export_value')))
    
    fast = [x for x in fast if x['imp'] - x['exp'] > 0] 
    
    # For convenience
    for x in fast: x['net'] = x['imp'] - x['exp']
                                                 
    build = [{"year":e['year'],"item_id":e['destination'], "name":e['destination__name_en'], 
              "abbr":e['destination__name_3char'], "value":e['net']} for e in fast]
    
  elif trade_flow == "export":  
    fast = list(raw.filter(export_value__gt=0).values('destination','year',
                                                      'destination__name_en',
                                                     'destination__name_3char').annotate(exp=Sum('export_value')))
    
    build = [{"year":e['year'],"item_id":e['destination'], "name":e['destination__name_en'], 
              "abbrv":e['destination__name_3char'], "value":e['exp']} for e in fast]                                                
    
  else:
    fast = list(raw.filter(import_value__gt=0).values('destination','year',
                                                  'destination__name_en',
                                                  'destination__name_3char').annotate(imp=Sum('import_value')))                                              
    
    build = [{"year":e['year'],"item_id":e['destination'], "name":e['destination__name_en'], 
              "abbr":e['destination__name_3char'], "value":e['imp']} for e in fast]

  """Set article variable for question """
  article = "to" if trade_flow == "export" else "from"
  
  # Set query params with our changes (session variable choices)
  query_params = request.GET.copy()
  query_params["lang"] = lang
  query_params["product_classification"] = classification
  
  json_response = {}
  json_response["data"] = build            
  json_response["attr_data"] = Country.objects.get_all(lang)
  json_response["class"] =  classification
  json_response["country1"] = origin.to_json()
  json_response["title"] = get_question("csay", trade_flow=trade_flow,origin=origin)#"Where does %s %s %s?" % (origin.name, trade_flow, article)
  json_response["year"] = year
  json_response["item_type"] = "country"
  json_response["app_type"] = "csay"
  json_response["other"] = query_params
  
  """Return to browser as JSON for AJAX request"""
  return HttpResponse(json.dumps(json_response))

def api_ccsy(request, classification, trade_flow, origin, destination, year):
  # Defaulting for the moment until we have the session variable 
  lang = "en"
  
  # Country
  origin = get_country(origin)
  if origin is None:
    raise Exception("Origin country does not exist.")
  destination = get_country(destination)
  if destination is None:
    raise Exception("Destination country does not exist")
  
  ## Year
  years_available = get_years(classification)
  
  # Article of speach 
  article = "to" if trade_flow == "export" else "from"


  ## Clasification & Django Data Call
  if classification == "sitc4":
    raw = Sitc4_ccpy.objects.filter(origin=origin.id).filter(destination=destination.id)
  elif classification == "hs4":
    raw = Hs4_ccpy.objects.filter(origin=origin.id).filter(destination=destination.id)
  else:
    raise Exception("Dataset not supported.")
    
  
    
  # Trade flow - defaults to import if invalid  
  if trade_flow == "net_export":
    fast = list(raw.values('year','product','product__code','product__name_en',
                  'export_value','import_value'))
    # Remove Negitives
    fast = [x for x in fast if x['export_value'] - x['import_value'] > 0]
    # Set set for convenience 
    for x in fast: x['net'] = x['export_value'] - x['import_value']
    
    build = [{"year":e['year'],"item_id":e['product'],"abbr":e['product__code'],
              "name":e['product__name_en'], "value":e['net']} for e in fast]
    
  elif trade_flow == "net_import":
    fast = list(raw.values('year','product','product__code','product__name_en',
                           'export_value','import_value'))
    # Remove Negitives
    fast = [x for x in fast if x['import_value'] - x['export_value'] > 0]
    # Set set for convenience 
    for x in fast: x['net'] = x['import_value'] - x['export_value']
    
    build = [{"year":e['year'],"item_id":e['product'],"abbr":e['product__code'],
              "name":e['product__name_en'], "value":e['net']} for e in fast]

  elif trade_flow == "export":
    exp = raw.filter(export_value__gt=0)
    fast = list(exp.values('year','product','product__code','product__name_en',
                  'export_value','import_value'))
    
    build = [{"year":e['year'],"item_id":e['product'],"abbr":e['product__code'],
              "name":e['product__name_en'], "value":e['export_value']} for e in fast]
  else:
    exp = raw.filter(import_value__gt=0)
    fast = list(raw.values('year','product','product__code','product__name_en',
                  'export_value','import_value'))
    
    build = [{"year":e['year'],"item_id":e['product'],"abbr":e['product__code'],
              "name":e['product__name_en'], "value":e['import_value']} for e in fast]
    
    
  
  # Set query params with our changes
  query_params = request.GET.copy()
  query_params["lang"] = lang
  query_params["product_classification"] = classification
  
  # Prepare JSON response
  json_response = {}
  json_response["data"] = build
  json_response["attr_data"] = Sitc4.objects.get_all(lang) if classification == "sitc4" else Hs4.objects.get_all(lang)
  json_response["country1"] = origin.to_json()
  json_response["country2"] = destination.to_json()
  json_response["title"] = get_question("ccsy", trade_flow=trade_flow,origin=origin,destination=destination)
  json_response["class"] =  classification
  json_response["year"] = year
  json_response["item_type"] = "product"
  json_response["app_type"] = "ccsy"
  json_response["other"] = query_params
  
  """Return to browser as JSON for AJAX request"""
  return HttpResponse(json.dumps(json_response))
  
def api_cspy(request, classification, trade_flow, origin, product, year):
  lang = "en"
  total_val={}
  #  Sanity Checks
  
  ## Country
  origin = get_country(origin)
  if origin is None:
    raise Exception("Country Does not Exist.")
  
  ## Product
  product = get_product(product,classification)
  if product is None:
    raise Exception("Product Does not Exist.")
  
  ## Year
  years_available = get_years(classification)
    
  ## Clasification & Django Data Call
  if classification == "sitc4":
    raw = Sitc4_ccpy.objects.filter(origin=origin.id).filter(product=product.id)
  elif classification == "hs4":
    raw = Hs4_ccpy.objects.filter(origin=origin.id).filter(product=product.id)
  else:
    raise Exception("Dataset not supported.")
  
  
  
  # Article of speech
  article = "to" if trade_flow == "export" else "from"
   
  if trade_flow == "net_export":
    fast = list(raw.filter(export_value__gt=0).values('destination','year',
                                                       'destination__name_en',
                                                       'destination__name_3char').annotate(imp=Sum('import_value'),
                                                                                           exp=Sum('export_value')))
     
    fast = [x for x in fast if x['exp'] - x['imp'] > 0]
    # For convenience
    for x in fast: x['net'] = x['exp'] - x['imp']
     
    build= [{"year":e['year'],"item_id":e['destination'],"abbr":e['destination__name_3char'],
               "name":e['destination__name_en'], "value":e['net']} for e in fast]
     
  elif trade_flow == "net_import":
    fast = list(raw.filter(import_value__gt=0).values('destination','year',
                                                       'destination__name_en',
                                                       'destination__name_3char').annotate(imp=Sum('import_value'),
                                                                                           exp=Sum('export_value')))
    fast = [x for x in fast if x['imp'] - x['exp'] > 0]
     # For convenience
    for x in fast: x['net'] = x['imp'] - x['exp']
     
    build = [{"year":e['year'],"item_id":e['destination'],"abbr":e['destination__name_3char'],
               "name":e['destination__name_en'], "value":e['net']} for e in fast]
   
  elif trade_flow == "export":
    fast = list(raw.filter(export_value__gt=0).values('destination','year',
                                                       'destination__name_en',
                                                       'destination__name_3char').annotate(exp=Sum('export_value')))
     
    build = [{"year":e['year'],"item_id":e['destination'],"abbr":e['destination__name_3char'],
               "name":e['destination__name_en'], "value":e['exp']} for e in fast]
   
  else:
    fast = list(raw.filter(import_value__gt=0).values('destination','year',
                                                      'destination__name_en',
                                                      'destination__name_3char').annotate(imp=Sum('import_value')))
    
    build= [{"year":e['year'],"item_id":e['country'],"abbr":e['destination__name_3char'],
              "name":e['destination__name_en'], "value":e['imp']} for e in fast]
    
  
  # Set query params with our changes
  query_params = request.GET.copy()
  query_params["lang"] = lang
  query_params["product_classification"] = classification
  """Prepare JSON response"""
  json_response = {}
  json_response["data"] = build
  json_response["attr_data"] = Country.objects.get_all(lang)
  json_response["title"] = get_question("casy", trade_flow=trade_flow,origin=origin,product=product)#"Where does %s %s %s %s?" % (origin.name, trade_flow, product.name_en, article)
  json_response["country1"] = origin.to_json()
  json_response["product"] = product.to_json()
  json_response["class"] =  classification
  json_response["year"] = year
  json_response["item_type"] = "country"
  json_response["app_type"] = "cspy"
  json_response["other"] = query_params

  ## Return to browser as JSON for AJAX request ##
  return HttpResponse(json.dumps(json_response))

def api_complex(request,origin,year):
  # import time
  # start = time.time()
  
  # If I don't set this things are defaulting to the original db. But this Module calls redesign at the top?
  from redesign.models import *
  
  origin = get_country(origin)
  if origin is None:
    raise Exception("Country Does not Exist.")
  
  relation = Hs4_cpy.objects.filter(country=origin.id)  
  attr_list = list(Hs4.objects.all().values('code','name')) #.extra(where=['CHAR_LENGTH(code) = 2'])
  attr = {}
  for i in attr_list: 
    attr[i['code']] = i
  
  # years = year.split('.')
  # if len(years) < 2:
  #   years.append(years[0])
  
  comp_list = list(Hs4_Py.objects.values())
  complexity = {}
  for i in comp_list: 
    complexity[i['product_id']] = i
  #import time
  #start = time.time()
  build_response = [{'country':i['country_id__name_3char'], 
                     'name': i['product_id__name_en'],
                     'color': i['product_id__community_id__color'],
                     'community': i['product_id__community_id'],
                     'community_name':i['product_id__community_id__name'],
                     # 'nesting_0': {'id':str(i['product_id__community_id']),
                      #              'name':i['product_id__community_id__name']},
                     # 'nesting_1': {'id': str(i['product_id__code'])[:2],
                      #              'name': attr.get(code=str(i['product_id__code'])[:2]).name },
                     # 'nesting_2': {'id': str(i['product_id']),
                     #               'name': i['product_id__name_en']},
										 'id': i['product_id'],
                     'code': i['product_id__code'],       
                     #'complexity': Hs4_Py.objects.get(year=i['year'],product=i['product_id']).pci,
	                   'year':i['year'], 
										 'value':i['export_value'],
										 'val_usd': i['export_value'],
                     'rca':i['export_rca'],
                     'distance':i['distance']} for i in relation
					 																										#.filter(year__range=(years[0],years[1]))
																																.values('country_id__name_3char',
                                                                        'product_id',
                                                                        'product_id__name', 
                                                                        'product_id__name_en',
                                                                        'product_id__code',
                                                                        'product_id__community_id',
                                                                        'product_id__community_id__name',
                                                                        'product_id__community_id__color',
                                                                        'distance',
                                                                        'export_rca',
                                                                        'export_value',
                                                                        'year'
                                                                       )]

  # raise Exception(time.time() - start)
  return HttpResponse(json.dumps({"data":build_response,"attr":attr, "complex":complexity}))

def tree(request,origin,year):
  origin = get_country(origin)
  if origin is None:
    raise Exception("Country Does not Exist.")
  
  # Return page without visualization data
  return render_to_response("tree_local.html", {
     "origin": origin,
     "year":year
    }, context_instance=RequestContext(request))

def stack(request,origin,year,classification="hs4"):
  origin = get_country(origin)
  if origin is None:
    raise Exception("Country Does not Exist.")
  
  years = year.split('.')  
  year_start = years[0]
  year_end = years[1]
  
  # Return page without visualization data
  return render_to_response("stack_local.html", {
     "origin": origin,
     "year":year,
     "year_start": year_start,
     "year_end": year_end
    }, context_instance=RequestContext(request))
   
    
def scatter(request,origin,year):
  origin = get_country(origin)
  if origin is None:
    raise Exception("Country Does not Exist.")
     
  # Return page without visualization data
  return render_to_response("scatter_local.html", {
     "origin": origin,
     "year":year
    }, context_instance=RequestContext(request))
def network(request,origin,year):
  origin = get_country(origin)
  if origin is None:
    raise Exception("Country Does not Exist.")
     
  # Return page without visualization data
  return render_to_response("network_local.html", {
     "origin": origin,
     "year":year
    }, context_instance=RequestContext(request))    
    
    
  
def api_cepii(request,origin):
  ## Country
  origin = get_country(origin)
  if origin is None:
    raise Exception("Country Does not Exist.")
    
  # Present
  present = Hs4_Cepii.objects.filter(iso=origin.name_3char,present=1).values()
  # Absent
  absent = Hs4_Cepii.objects.filter(iso=origin.name_3char,absent=1).values()
  # Neither present nor Absent
  floating = Hs4_Cepii.objects.filter(iso=origin.name_3char,absent=0,present=0).values()
  
  build_pr = [{"product_name":e['product'],"abbr":e['iso'],
             "name":e['country'], "m_resid":e['m_resid'],"hs4":e['hs4']} for e in present]
  
  build_ab = [{"product_name":e['product'],"abbr":e['iso'],
             "name":e['country'], "m_resid":e['m_resid'],"hs4":e['hs4']} for e in absent]
  
  build_fl = [{"product_name":e['product'],"abbr":e['iso'],
             "name":e['country'], "m_resid":e['m_resid'],"hs4":e['hs4']} for e in floating]
             
  json_response = {}
  json_response["present"] = build_pr
  json_response["absent"] = build_ab
  json_response["floating"] = build_fl   
  json_response["origin"] = origin.to_json() 
  
  ## Return to browser as JSON for AJAX request ##
  return HttpResponse(json.dumps(json_response))      


def predict(request, country):
  ## Country
  origin = get_country(country)
  if origin is None:
    raise Exception("Country Does not Exist.")

  ### Present
  present = list(Hs4_Cepii.objects.filter(iso=country,present=1).order_by('-m_resid'))
  
  disappear = [{"product":e.product,"abbr":e.iso,"hs4":e.hs4,
              "m_resid":e.m_resid} for e in present[:10]]
  
  remain_present = [{"product":e.product,"abbr":e.iso,"hs4":e.hs4,
              "m_resid":e.m_resid} for e in present[-10:]]
  
  
  ### Absent
  absent = list(Hs4_Cepii.objects.filter(iso=country,absent=1).order_by('m_resid'))
  
  appear = [{"product":e.product,"abbr":e.iso,"hs4":e.hs4,
              "m_resid":e.m_resid} for e in absent[:10]]
  
  remain_absent = [{"product":e.product,"abbr":e.iso,"hs4":e.hs4,
              "m_resid":e.m_resid} for e in absent[-10:]]
              
  everybody = []
  
  for i in appear[:5]: everybody.append(i)
  for i in remain_absent[-5:]: everybody.append(i)
  for i in disappear[:5]: everybody.append(i)
  for i in remain_present[-5:]: everybody.append(i)
  
  
  
  
  all_products = Hs4_Cepii.objects.filter(iso=country).order_by('-m_hat')
  rcas =  [item.rca for item in all_products.filter(rca__gt=0)]
  
  
  mh_p = list(all_products.filter(present=1).values())
  mh_a = list(all_products.filter(absent=1).values())
  
  
              
  json_response = {}
  
  json_response["disappear"] = disappear
  json_response["appear"] = appear
  json_response["remain_present"] = remain_present
  json_response["remain_absent"] = remain_absent
      
                  
  return render_to_response("redesign/predict.html",{'country':origin, 'cepii_present':present,
                            'cepii_absent':absent,'datu':json.dumps(json_response), 'every':json.dumps(everybody),
                            'mh_ph': json.dumps(mh_p[:6]), 'mh_pl': json.dumps(mh_p[-6:]),
                            'mh_ah':json.dumps(mh_a[:6]),'mh_al':json.dumps(mh_a[-6:]),
                            'rcas':json.dumps(rcas), 'all_prod':json.dumps(list(all_products.filter(rca__gt=0).values()))}, context_instance=RequestContext(request))    
  
  