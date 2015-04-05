from django.conf.urls import url, patterns

from . import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^(?P<pk>\d+)/$', views.forum, name='forum'),
    url(r'^thread/(?P<pk>\d+)/$', views.thread, name='thread'),
    url(r'^add_thread/(?P<pk>\d+)/$', views.add_thread, name='add_thread'),
    url(r'^thread/add_post/(?P<pk>\d+)/$', views.add_post, name='add_post'),
    url(r'^create_forum/$', views.create_forum, name='create_forum'),
    url(r'^accounts/edit_profile/(?P<pk>\d+)/$', views.edit_profile, name='edit_profile'),
)
