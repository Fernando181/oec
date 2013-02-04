# Create your views here.

from django.http import HttpResponse
from redesign.models import *

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
  
  # get distince years from db, different for diff product classifications
  years_available = list(Sitc4_cpy.objects.values_list("year", flat=True).distinct()) if classification == "sitc4" else list(Hs4_cpy.objects.values_list("year", flat=True).distinct())
  years_available.sort()
  
  
  
  output = "Redesign says Hello World!"
  return HttpResponse(years_available)


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