from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from rango import views

urlpatterns = patterns('',

    url(r'^admin/', include(admin.site.urls)),
    url(r'^rango/', include('rango.urls')), # ADD THIS NEW TUPLE!
    url(r'^$', views.index, name='index'),
    url(r'^about/$', views.about, name='about'),
    url(r'^rango/category/(?P<category_name_slug>[\w\-]+)/$', views.category, name='category'),)  # New!

if settings.DEBUG:
    urlpatterns += patterns(
        'django.views.static',
        (r'^media/(?P<path>.*)',
        'serve',
        {'document_root': settings.MEDIA_ROOT}), )