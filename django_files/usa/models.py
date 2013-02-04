from django.db import models
from observatory.models import *

class County(models.Model):
    id = models.IntegerField(primary_key=True)
    fipstate = models.IntegerField()
    fipscounty = models.IntegerField()
    fips = models.CharField(max_length=33)
    state = models.CharField(max_length=9)
    name = models.CharField(max_length=150)
    
    def __unicode__(self):
  	  return self.name  
    
    class Meta:
        db_table = u'usa_county'

class State(models.Model):
    name = models.CharField(max_length=300)
    abbr = models.CharField(max_length=33)
    fips = models.IntegerField()
    
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
    naics6 = models.IntegerField()
    name = models.CharField(max_length=765)
    description = models.TextField()
    
    def __unicode__(self):
  	  return self.name
    
    class Meta:
        db_table = u'usa_naics'

class NaicsCounty(models.Model):
    id = models.IntegerField(primary_key=True)
    year = models.IntegerField()
    state = models.IntegerField()
    county = models.IntegerField()
    fips = models.CharField(max_length=33)
    naics = models.IntegerField()
    employees = models.IntegerField()
    payroll = models.IntegerField()
    rca_employee = models.FloatField()
    rca_payroll = models.FloatField()
    
    def __unicode__(self):
  	  return "%s,%s,%s" % (self.state,self.county,self.naics,self.year) 
    
    
    class Meta:
        db_table = u'usa_naics_county'

class NaicsMsa(models.Model):
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