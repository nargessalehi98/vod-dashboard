"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from config.logger import log_error
from dashboard.urls import dashboard_routing
from data_control.urls import data_routing
from uploader.urls import uploader_routing
from internal.urls import internal_routing
from admin_control.urls import admin_routing


@api_view()
def not_found(request, *args, **kwargs):
    log_error('URL not found', request=request)
    return Response(data={'detail': 'not found'}, status=status.HTTP_404_NOT_FOUND)


urlpatterns = [
    path('dashboard', dashboard_routing),
    path('uploader', uploader_routing),
    path('data', data_routing),
    path('internal', internal_routing),
    path('admin', admin_routing),
    path('', not_found)
]
