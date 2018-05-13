from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from webpage import views

app_name = 'webpage'
urlpatterns = [
   # ex: /webpage/
    url(r'^$', views.home, name='home'),
    url(r'^signup/', views.signup, name='signup'),
    url(r'^create-project/', views.projectForm, name='projectForm'),
    url(r'^edit-project/(?P<id>\d+)/$', views.projectForm, name='projectForm'),
    url(r'^delete-project/(?P<id>\d+)/$', views.deleteProject, name='deleteProject'),
    url(r'^invite-scientist/(?P<id>\d+)/$', views.inviteScientist, name='inviteScientist'),
    url(r'^workflow/$', views.WorkflowList.as_view()),
    url(r'^workflow/(?P<pk>[0-9]+)$', views.WorkflowDetail.as_view()),
    url(r'^projects/$', views.ProjectList.as_view()),
]
