from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from rango import views

urlpatterns = patterns('',

	url(r'^admin/', include(admin.site.urls)),
	url(r'^rango/', include('rango.urls')), 
	url(r'^$', views.index, name='index'),
	url(r'^about/$', views.about, name='about'),
	url(r'^rango/category/(?P<category_name_slug>[\w\-]+)/$', views.category, name='category'),
	url(r'^rango/add_category/$', views.add_category, name='add_category'), 
	url(r'^rango/category/(?P<category_name_slug>[\w\-]+)/add_page/$', views.add_page, name='add_page'),
	url(r'^rango/register/$', views.register, name='register'),
	url(r'^rango/login/$', views.user_login, name='login'),
	url(r'^rango/restricted/', views.restricted, name='restricted'),
	url(r'^rango/logout/$', views.user_logout, name='logout'),
	)  # New!

if settings.DEBUG:
    urlpatterns += patterns(
        'django.views.static',
        (r'^media/(?P<path>.*)',
        'serve',
        {'document_root': settings.MEDIA_ROOT}), )