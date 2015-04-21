from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^students/', include('students.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^lectures/', include('lectures.urls')),
)
