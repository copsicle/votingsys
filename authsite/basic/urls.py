from django.urls import path
#from django.shortcuts import redirect
from . import views
#from django.views.generic.base import RedirectView


app_name = 'basic'
urlpatterns = [
    path('', views.index, name='index'),
    path('advanced/', views.advanced, name='advanced'),
    path('voted/<slug:ses_id>', views.voted, name='voted'),
]
