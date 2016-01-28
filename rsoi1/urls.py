from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^rsoi1/redirect', 'rsoi1.views.redirect_view'),
    url(r'^rsoi1/app', 'rsoi1.views.app'),
    url(r'^rsoi1/logout', 'rsoi1.views.logout'),
)