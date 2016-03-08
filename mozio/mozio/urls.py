from django.conf.urls import url, include
from rest_api import views


urlpatterns = [
    url(r'^api/', views.Register.as_view()),
    url(r'^api2/', views.Polygon.as_view()),
]
