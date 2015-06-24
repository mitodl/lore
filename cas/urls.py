"""CAS URL configuration"""
from django.conf.urls import url

urlpatterns = [
    url(r'^login$', 'django_cas_ng.views.login', name="cas_login"),
    url(r'^logout$', 'django_cas_ng.views.logout', name="cas_logout"),
]
