from django.urls import path
from . import views

app_name = 'landing'

urlpatterns = [
    path('', views.download_app, name='download_app'),
] 