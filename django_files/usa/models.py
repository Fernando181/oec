from django.db import models
from observatory.models import *

class County(models.Model):
    id = models.IntegerField(primary_key=True)
    state_id = models.IntegerField(null=True, blank=True)
    fips_county_id = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=765, blank=True)
    slug = models.CharField(max_length=765, blank=True)
    
    def __unicode__(self):
  	  return self.name  
    
    class Meta:
        db_table = u'usa_county'

class State(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=765, blank=True)
    abbr = models.CharField(max_length=765, blank=True)
    fips = models.IntegerField(null=True, blank=True)
    
    def __unicode__(self):
  	  return self.name
    
    class Meta:
        db_table = u'usa_state'        

class Msa(models.Model):
    id = models.IntegerField(primary_key=True)
    code = models.IntegerField()
    name = models.CharField(max_length=765)
    population = models.IntegerField(null=True, blank=True)
    metro = models.IntegerField(null=True, blank=True)
    abbr = models.CharField(max_length=36, blank=True)
    state = models.CharField(max_length=150)
    
    def __unicode__(self):
  	  return self.name
      
    class Meta:
        db_table = u'usa_msa'

class Naics(models.Model):
    id = models.IntegerField(primary_key=True)
    naics = models.IntegerField()
    name = models.CharField(max_length=765)
    description = models.TextField()
    
    def __unicode__(self):
  	  return self.name
    
    class Meta:
        db_table = u'usa_naics'

class Naics_County(models.Model):
    id = models.IntegerField(primary_key=True)
    year = models.IntegerField(null=True, blank=True)
    county_id = models.IntegerField(null=True, blank=True)
    naics = models.IntegerField(null=True, blank=True)
    employees = models.IntegerField(null=True, blank=True)
    payroll = models.IntegerField(null=True, blank=True)
    rca_employee = models.CharField(max_length=765, blank=True)
    rca_payroll = models.CharField(max_length=765, blank=True)
    
    def __unicode__(self):
  	  return "%s,%s,%s" % (self.county_id,self.naics,self.year) 
    
    
    class Meta:
        db_table = u'usa_naics_county'

class Naics_Msa(models.Model):
    id = models.IntegerField(primary_key=True)
    year = models.IntegerField()
    msa = models.IntegerField()
    naics = models.IntegerField()
    employees = models.IntegerField()
    payroll = models.IntegerField()
    rca_employment = models.FloatField()
    rca_payroll = models.FloatField()
    establishments = models.IntegerField()
    class Meta:
        db_table = u'usa_naics_msa'
        
    def __unicode__(self):
  	  return "%s,%s" % (self.msa,self.naics)    