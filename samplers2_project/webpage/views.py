from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from webpage.forms import SignUpForm, ProjectForm
from django.db import transaction
from webpage.models import Project
from django.shortcuts import get_object_or_404, redirect, render
from webpage.models import Workflow
from webpage.serializers import WorkflowSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
#import pdb; pdb.set_trace()


@login_required
def home(request):
    projects_list = Project.objects.filter(
        owner_id=request.user.profile.id, deleted=False)
    context = {'projects_list': projects_list}
    return render(request, 'webpage/home.html', context)


@login_required
def deleteProject(request, id=None):
    if id:
        project = get_object_or_404(Project, pk=id)
        # import pdb; pdb.set_trace()
        if project.owner != request.user.profile:
            return HttpResponseForbidden()
    else:
        project = Project(owner=request.user.profile)
    project.deleted = True
    project.save()
    return redirect('home')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.profile.first_name = form.cleaned_data.get('first_name')
            user.profile.last_name = form.cleaned_data.get('last_name')
            user.profile.institucion = form.cleaned_data.get('institucion')
            user.profile.email = form.cleaned_data.get('email')
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'webpage/signup.html', {'form': form})


@login_required
def projectForm(request, id=None):
    if id:
        project = get_object_or_404(Project, pk=id)
        if project.owner != request.user.profile:
            return HttpResponseForbidden()
    else:
        project = Project(owner=request.user.profile)
    form = ProjectForm(request.POST or None, instance=project)
    if request.POST and form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user.profile
        project.save()
        return redirect('home')
    return render(request, 'webpage/projectForm.html', {'form': form})


class WorkflowList(APIView):
    """
    List all workflow, or create a new snippet.
    """
    def get(self, request, format=None):
        Workflows = Workflow.objects.all()
        serializer = WorkflowSerializer(Workflows, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = WorkflowSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class WorkflowDetail(APIView):
    """
    Retrieve, update or delete a workflow instance.
    """
    def get_object(self, pk):
        try:
            return Workflow.objects.get(pk=pk)
        except Workflow.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        workflow = self.get_object(pk)
        serializer = WorkflowSerializer(workflow)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        workflow = self.get_object(pk)
        serializer = WorkflowSerializer(workflow, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        workflow = self.get_object(pk)
        workflow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
