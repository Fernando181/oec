from usa.models import *

def get_app_type(origin, destination, industry, year):
  # location / all / show / year
  if destination == "all" and industry == "show":
    return "casy"
  # show / all / industry / year
  elif origin == "show":
    return "sapy"
  else:
    return "casy"  

def get_county(origin,classification):
  # check class, currently only really support for county level data
  if classification == "county":
    try:
      origin = County.objects.get(slug=origin)
    except County.DoesNotExist:
      origin = None
  elif classification == "msa":
    try:
      origin = Msa.objects.get(code=origin)
    except Msa.DoesNotExist:
      origin = None
    
  return origin  
  
def get_industry(industry):
  if industry != "show":
    try:
      industry = Naics.objects.get(naics=industry)
    except Naics.DoesNotExist:
      industry = None

  return industry
  
def get_years(classification):
  # get distince years from db, different for diff product classifications
  if classification == "county":
    years_available = list(Naics_County.objects.values_list("year", flat=True).distinct())
  elif classification == "msa":
    years_available = list(Naics_Msa.objects.values_list("year", flat=True).distinct())
  return years_available
