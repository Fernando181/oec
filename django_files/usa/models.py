from django.db import models
from observatory.models import *

# Create your models here.
class State(models.Model):
    name = models.CharField(max_length=300)
    abbr = models.CharField(max_length=33)
    fips = models.IntegerField(primary_key=True)
        
    def __unicode__(self): 
      return self.name    

class County(models.Model):
    id = models.IntegerField(primary_key=True)
    fipstate = models.IntegerField()
    fipscounty = models.IntegerField()
    fips = models.CharField(max_length=11)
    state = models.CharField(max_length=3)
    name = models.CharField(max_length=50)
  	
    def __unicode__(self):
  	  return self.name   
      

class Msa(models.Model):
    id = models.IntegerField(primary_key=True)
    code = models.IntegerField()
    name = models.CharField(max_length=255)
    population = models.IntegerField()
    metro = models.IntegerField()
    abbr = models.CharField(max_length=12)
    state = models.CharField(max_length=50)
    
    def __unicode__(self):
  	  return self.name
      
      
class Naics(models.Model):
    id = models.IntegerField(primary_key=True)
    naics6 = models.IntegerField()
    name = models.CharField(max_length=255)
    description = models.TextField()
    
    def __unicode__(self):
  	  return self.name
       

class Naics_County(models.Model):
    id = models.IntegerField(primary_key=True)
    year = models.IntegerField()
    state = models.IntegerField()
    county = models.IntegerField()
    fips = models.CharField(max_length=11)
    naics = models.IntegerField()
    employees = models.IntegerField()
    payroll = models.IntegerField()
    rca_employee = models.FloatField()
    rca_payroll = models.FloatField()
    
    
    def __unicode__(self):
  	  return "%s,%s,%s" % (self.state,self.county,self.naics,self.year) 

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
    
    def __unicode__(self):
  	  return "%s,%s" % (self.msa,self.naics)
      
      
      
      
    