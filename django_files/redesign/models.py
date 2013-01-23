from django.db import models
from django.db.models import Sum

###############################################################################
# country tables
###############################################################################
class Country_region(models.Model):
	name = models.CharField(max_length=50, null=True)
	color = models.CharField(max_length=7, null=True)
	text_color = models.CharField(max_length=7, null=True)

	def __unicode__(self):
		return self.name

class Country_manager(models.Manager):
	
	def filter_lang(self, lang):
		return self.extra(select={"name": "name_"+lang})
	
	def get_all(self, lang):
		
		if type(lang) == bool:
			lang = "en"
		lang = lang.replace("-", "_")
		
		countries = self.filter_lang(lang)
		countries = countries.filter(region__isnull=False, name_3char__isnull=False, name_2char__isnull=False).order_by("name_"+lang)
		return list(countries.values(
			"id",
			"name",
			"name_3char",
			"name_2char",
			"region_id",
			"region__color",
			"region__name",
			"region__text_color"
		))

class Country(models.Model):
	name = models.CharField(max_length=200)
	name_numeric = models.PositiveSmallIntegerField(max_length=4, null=True)
	name_2char = models.CharField(max_length=2, null=True)
	name_3char = models.CharField(max_length=3, null=True)
	continent = models.CharField(max_length=50, null=True)
	region = models.ForeignKey(Country_region, null=True)
	capital_city = models.CharField(max_length=100, null=True)
	longitude = models.FloatField(null=True)
	latitude = models.FloatField(null=True)
	coordinates = models.TextField(null=True)
	name_ar = models.TextField(null=True)
	name_de = models.TextField(null=True)
	name_el = models.TextField(null=True)
	name_en = models.TextField(null=True)
	name_es = models.TextField(null=True)
	name_fr = models.TextField(null=True)
	name_he = models.TextField(null=True)
	name_hi = models.TextField(null=True)
	name_it = models.TextField(null=True)
	name_ja = models.TextField(null=True)
	name_ko = models.TextField(null=True)
	name_nl = models.TextField(null=True)
	name_ru = models.TextField(null=True)
	name_pt = models.TextField(null=True)
	name_tr = models.TextField(null=True)
	name_zh_cn = models.TextField(null=True)
	
	def __unicode__(self):
		return self.name
	
	def to_json(self):
		return {
			"name": self.name_en,
			"name_3char": self.name_3char}
	
	objects = Country_manager()
  
class Cy(models.Model):
	country = models.ForeignKey(Country)
	year = models.PositiveSmallIntegerField(max_length=4)
	eci = models.FloatField(null=True)
	eci_rank = models.PositiveSmallIntegerField(max_length=4)
	oppvalue = models.FloatField(null=True)

	def __unicode__(self):
		return "%s rank: %d" % (self.country.name, self.eci_rank)