from observatory.models import *

def get_years(classification):
  # get distince years from db, different for diff product classifications
  if classification == "sitc4":
    years_available = list(Sitc4_cpy.objects.values_list("year", flat=True).distinct())
  elif classification == "hs4":
    years_available = list(Hs4_cpy.objects.values_list("year", flat=True).distinct())
  return years_available