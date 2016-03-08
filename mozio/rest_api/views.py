from django.shortcuts import render
# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import Http404, HttpResponse, HttpResponseRedirect,HttpResponseServerError
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from .models import ServiceProfile,Service
# from django.forms.models import modelform_factory
from django.views.generic.edit  import CreateView
# Create your views here.

import geojson
import json
import ast

class Register(CreateView):
	# @method_decorator(csrf_exempt)
	@csrf_exempt
	def dispatch(self, request, *args, **kwargs):
		return super(Register, self).dispatch(request, *args, **kwargs)

	def get(self,request, *args, **kwargs):
		results = list()
		response = list()
		Names = request.GET.getlist('Name')
		if not Names:
			results = ServiceProfile.objects.all()
			response = json.loads(serializers.serialize('json',results))
			return JsonResponse({'Response':response})
		for Name in Names:
			try:
				results.append(ServiceProfile.objects.all().filter(Name=Name))
			except Exception:
				return Http404('User Name Not found')
		for result in results:
			data = json.loads(serializers.serialize('json',result))
			response.append(data)
		return JsonResponse({'Response':response})

	def post(self,request,*args, **kwargs):
		Name = request.POST.get('Name')
		Phone = request.POST.get('Phone')
		Language = request.POST.get('Language')
		Email = request.POST.get('Email')
		Currency = request.POST.get('Currency')
		try:
			serviceProfile = ServiceProfile.objects.update_or_create(
				Name=Name,Phone=Phone,Language=Language,Email=Email,Currency=Currency)
		except Exception as e:
			return HttpResponseServerError('<h1>Server Error (500)</h1>') 
		return JsonResponse({'response':'Success'})

	def put(self,request,*args, **kwargs):
		data = request.read()
		data = [d.split('=')for d in data.split('&')]
		data = {t[0]:t[1] for t in data}
		try:
			result = ServiceProfile.objects.get(Email=data['Email'].replace('%40','@'))
		except ObjectDoesNotExist:
			return HttpResponse(json.dumps({'Response':'Fail'}),content_type="application/json",status=404)
		result.Name = data['Name']
		result.Phone = data['Phone']
		result.Language = data['Language']
		result.Currency = data['Currency']
		result.save()
		return JsonResponse({'Response':'Success'})
		
	def delete(self, request,*args,**kwargs):
		data = request.read()
		data = [d.split('=')for d in data.split('&')]
		for d in data:
			if d[0] == 'Email':
				data = d[1]
		try:
			result = ServiceProfile.objects.get(Email=data.replace('%40','@'))
		except ObjectDoesNotExist:
			return HttpResponse(json.dumps({'Response':'Record not found'}),content_type="application/json",status=404)
		return JsonResponse({'Response':'Success'})


class Polygon(CreateView):
	# @method_decorator(csrf_exempt)
	@csrf_exempt
	def dispatch(self, request, *args, **kwargs):
		return super(Polygon, self).dispatch(request, *args, **kwargs)

	def get(self,request, *args, **kwargs):
		Names = request.GET.getlist('Name')
		Service_ids = request.GET.getlist('Service_id')
		results = list()
		response = list()
		if not Names or not Service_ids:
			return HttpResponse({'Response':'Name and Service id required'},status=500)
		if len(Names) != len(Service_ids):
			return HttpResponse({'Response':'Either Name or Service_id missing'},status=500)
		for Name,Service_id in zip(Names,Service_ids):
			try:
				Service_id = ServiceProfile.objects.get(pk=Service_id)
			except ObjectDoesNotExist:
				return HttpResponse(json.dumps(
					{'Response':'Record not found'}),content_type="application/json",status=404)
			
			result = Service.objects.all().filter(Name=Name).filter(Service_id=Service_id)
			if not result:
				continue
			results.append(result)
		if not results:
			return HttpResponse(json.dumps({'Response':'Polygon Name Not found'}),
			content_type="application/json",status=404)
		georesult = dict()
		for result in results:
			polygon_object = polygon(result[0].geos).geo
			georesult['geos'] = polygon_object
			georesult['Name'] = result[0].Name
			georesult['Price'] = result[0].Price
			georesult['Service_id'] = result[0].Service_id.id
			response.append(georesult)
		return JsonResponse({'Response':response})

	def post(self,request,*args, **kwargs):
		geos = json.dumps(request.POST.get('geos'))
		Service_id = request.POST.get('Service_id')
		Name = request.POST.get('Name')
		Price = request.POST.get('Price')
		try:
			Service_id = ServiceProfile.objects.get(id=Service_id)
		except ObjectDoesNotExist:
			return JsonResponse(json.dumps({'Response':'Service Profile Error'}),
				content_type='application/json',status=404)
		try:
			service = Service.objects.get(Service_id=Service_id,Name=Name)
		except ObjectDoesNotExist:
			service = Service(geos=geos,Service_id=Service_id,Name=Name,Price=float(Price))
			service.save()
		except Exception as e:
			return JsonResponse(json.dumps({'Response':'Error'}),content_type='application/json',status=500) 

		return JsonResponse({'Response':'Success'})

	def put(self,request,*args, **kwargs):
		data = request.read()
		data = [d.split('=')for d in data.split('&')]
		data = {t[0]:t[1] for t in data}
		data['geos'] = data['geos'].replace('%5B','[').replace('%2C',',').replace('%5D',']')
		try:
			Service_id = ServiceProfile.objects.get(id=data['Service_id'])
		except ObjectDoesNotExist:
			return HttpResponse(json.dumps({'Response':'Wrong Service Id'}),status=404,content_type='application/json')
		try:
			result = Service.objects.get(Name=data['Name'],Service_id=Service_id)
		except ObjectDoesNotExist:
			return HttpResponse(json.dumps({'Response':'Fail'}),content_type="application/json",status=404)
		result.geos = json.dumps(data['geos'])
		result.Name = data['Name']
		result.Price = data['Price']
		result.save()
		return JsonResponse({'Response':'Success'})

	def delete(self, request,*args,**kwargs):
		data = request.read()
		data = [d.split('=')for d in data.split('&')]
		for d in data:
			if d[0] == 'Service_id':
				data = d[1]
			if d[0] == 'Name':
				data2 = d[1]
		try: 
			Service_id = ServiceProfile.objects.get(id=data)
		except ObjectDoesNotExist:
			return HttpResponse(json.dumps({'Response':'Fail'}),content_type='application/json',status=404)
		try:
			result = Service.objects.get(Service_id=Service_id,Name=data2)
		except ObjectDoesNotExist:
			return HttpResponse(json.dumps({'Response':'Fail'}),content_type="application/json",status=404)
		result.delete()
		return JsonResponse({'Response':'Success'})


class polygon():
	def __init__(self,x):
		self.x = x
	@property	
	def geo(self):
		return {'type':'Feature','geometry':{'type':'polygon','coordinates':ast.literal_eval(self.x)}}