"""addressbook URL Configuration

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
#from django.contrib import admin
from django.contrib.auth import views as auth_views

from django.urls import path
from django.conf.urls import include, url
import contacts.views
from django.contrib import auth

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^$', contacts.views.ListContactView.as_view(),
        name='contacts-list',),
    url(r'^new$', contacts.views.CreateContactView.as_view(),
        name='contacts-new',),
    url(r'^edit/(?P<pk>\d+)/$', contacts.views.UpdateContactView.as_view(),
        name='contacts-edit',),
    url(r'^delete/(?P<pk>\d+)/$', contacts.views.DeleteContactView.as_view(),
        name='contacts-delete',),
    url(r'^(?P<pk>\d+)/$', contacts.views.ContactView.as_view(),
        name='contacts-view',),
    url(r'^edit/(?P<pk>\d+)/addresses$', contacts.views.EditContactAddressView.as_view(),
        name='contacts-edit-addresses',),
#    url('accounts/', include(('django.contrib.auth.urls', 'admin'), namespace='admin')),
    path('accounts/login/', auth_views.LoginView.as_view()),
    path('accounts/logout/', auth_views.LogoutView.as_view())
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
