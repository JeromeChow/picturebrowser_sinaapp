from django.conf.urls.defaults import *
from mysite import views
from mysite import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^mysite/', include('mysite.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),

    (r'^$', views.index),
    (r'^photogallary/$', views.photogallary),
    (r'^search/$', views.search),
    (r'^logout/$', views.logout),
    (r'^hello/$', views.hello),
    (r'^debug/$', views.debug),
    (r'^morefriends/$', views.morefriends),
    (r'^morepictures/$', views.morepictures),
    (r'^searchfriend/$', views.searchfriend),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve',{'document_root': settings.MEDIA_ROOT },name="media"),
)
