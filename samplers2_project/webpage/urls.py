from django.conf.urls import url

from . import views

app_name = 'webpage'
urlpatterns = [
   # ex: /webpage/
    url(r'^$', views.signup, name='signup'),
    
]
