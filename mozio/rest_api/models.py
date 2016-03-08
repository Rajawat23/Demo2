from djgeojson.fields import PolygonField

from django.db import models
# from django.contrib.gis.db import models as gs_models
from django.core.validators import RegexValidator
# Create your models here.

# Carrier User Table
class ServiceProfile(models.Model):
	Name = models.TextField()
	Email = models.EmailField()
	phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
	Phone  = models.CharField(validators=[phone_regex], blank=True,max_length=15)
	Language = models.CharField(max_length=10)
	Currency = models.CharField(max_length=10)

# Carrier User Service area addition
class Service(models.Model):
	geos = PolygonField()
	# objects = gs_models.GeoManager()
	Service_id = models.ForeignKey('ServiceProfile')
	Name = models.TextField()
	Price = models.DecimalField(max_digits=7,decimal_places=2)

# Create your models here.
