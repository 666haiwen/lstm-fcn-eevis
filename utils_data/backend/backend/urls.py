"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import include, path
from . import api
from . import views

api_urlpatterns = [
    path('tsne', api.get_tsne),
    path('birch', api.get_birch),
    path('forceInfo', api.get_forceInfo),
    path('busData', api.get_busData),
    path('busDistance', api.get_busDistance),
    path('corrcoef', api.get_corrcoef),
    path('sampleDis', api.get_sampleDis),
    path('busField', api.get_field),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index),
    path('api/', include(api_urlpatterns))
]
