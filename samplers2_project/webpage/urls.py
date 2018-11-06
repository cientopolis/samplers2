from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from webpage import views
from django.conf.urls.static import url, static
from django.conf import settings


app_name = 'webpage'
urlpatterns = [
   # ex: /webpage/
    url(r'^$', views.home, name='home'),
    url(r'^signup/', views.signup, name='signup'),
    url(r'^create-project/', views.createProject, name='createProject'),
    url(r'^edit-project/(?P<id>\d+)/$', views.editProject, name='editProject'),
    url(r'^delete-project/(?P<id>\d+)/$', views.deleteProject, name='deleteProject'),
    url(r'^invite-scientist/(?P<id>\d+)/$', views.inviteScientist, name='inviteScientist'),
    url(r'^show-results/(?P<id>\d+)/$', views.showResults, name='showResults'),
    url(r'^workflow/$', views.WorkflowList.as_view()),
    url(r'^workflow/(?P<pk>[0-9]+)$', views.WorkflowDetail.as_view()),
    url(r'^projects/$', views.ProjectList.as_view()),
    url(r'^project/(?P<pk>[0-9]+)$', views.ProjectDetail.as_view()),
    url(r'^workflow/(?P<pk>[0-9]+)/result$', views.WorkflowResult.as_view()),
    url(r'^create-workflow/(?P<id>\d+)/$', views.createWorkflow, name='createWorkflow'),
    url(r'^prueba/$', views.Prueba.as_view()),
    url(r'^login/$', views.Login.as_view()),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
