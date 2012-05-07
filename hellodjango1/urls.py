from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^login/?$', 'linkedin.views.oauth_login'),
    url(r'^logout/?$', 'linkedin.views.oauth_logout'),
    url(r'^login/authenticated/?$', 'linkedin.views.oauth_authenticated'),
    url(r'^$','linkedin.views.home'),
)

