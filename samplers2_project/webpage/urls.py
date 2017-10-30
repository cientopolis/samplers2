from django.conf.urls import url

from . import views

app_name = 'webpage'
urlpatterns = [
   # ex: /webpage/
    url(r'^$', views.home, name='home'),
    url(r'^signup/', views.signup, name='signup'),
    url(r'^create-project/', views.projectForm, name='projectForm'),
    url(r'^edit-project/(?P<id>\d+)/$', views.projectForm, name='projectForm'),
]
