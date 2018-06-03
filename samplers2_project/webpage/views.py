from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from webpage.forms import SignUpForm, ProjectForm
from django.db import transaction
from webpage.models import Project, ParticipantsGroup
from django.shortcuts import get_object_or_404, redirect, render
from webpage.models import Workflow
from webpage.serializers import *
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import pdb


@login_required
def home(request):
    projects_list = Project.objects.filter(
        participants__id=request.user.profile.id, deleted=False)
    context = {'projects_list': projects_list}
    return render(request, 'webpage/home.html', context)


@login_required
def deleteProject(request, id=None):
    if id:
        project = get_object_or_404(Project, pk=id)
        import pdb; pdb.set_trace()
        #Si el id del usuario no coincide con un id de la lista de usuarios del proyecto, devuelvo Forbidden
        if not(project.participants.filter(pk=request.user.profile.id).exists()):
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
def createProject(request, id=None):
    project = Project()
    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user.profile.user.username
        project.save()
        pg = ParticipantsGroup.objects.create(project = project, profile = request.user.profile)
        pg.is_owner = True
        pg.save()
        return redirect('home')
    return render(request, 'webpage/projectForm.html', {'form': form})

@login_required
def editProject(request, id=None):
    if id:
        project = get_object_or_404(Project, pk=id)
        #Si el id del usuario no coincide con un id de la lista de usuarios del proyecto, devuelvo Forbidden
        if not(project.participants.filter(pk=request.user.profile.id).exists()):
            return HttpResponseForbidden()
    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid():
        project = form.save()
        return redirect('home')
    return render(request, 'webpage/projectForm.html', {'form': form})

@login_required
def inviteScientist(request, id=None):
    if id:
        project = get_object_or_404(Project, pk=id)
        #Si el id del usuario no coincide con un id de la lista de usuarios del proyecto, devuelvo Forbidden
        if not(project.participants.filter(pk=request.user.profile.id).exists()):
            return HttpResponseForbidden()
    #else:


class WorkflowList(APIView):
    """
    List all workflow, or create a new workflow.
    """

    def get(self, request, format=None):
        workflows = Workflow.objects.all()
        serializer = WorkflowSerializer(Workflows, many=True)
        return Response({"data":serializer.data, "status_code": 200}, status = 200)

    def post(self, request, format=None):
        serializer = WorkflowSerializerPost(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "status_code":status.HTTP_201_CREATED}, status=status.HTTP_201_CREATED)
        return Response({"data":serializer.errors, "status_code": status.HTTP_400_BAD_REQUEST}, status = status.HTTP_400_BAD_REQUEST)


class WorkflowDetail(APIView):
    
    def get_object(self, pk):
        try:
            return Workflow.objects.get(pk=pk)
        except Workflow.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        workflow = self.get_object(pk)
        serializer = WorkflowSerializer(workflow)
        data = serializer.data
        index = 1
        for obj in data['steps']:
            obj["id"] = index
            index = index + 1
            pdb.set_trace()
            if (obj['step_type'] == StepType.SELECTONESTEP.value) | (obj['step_type'] == StepType.SELECTMULTIPLESTEP.value):
                id = 1
                pdb.set_trace()
                for option in obj['options_to_show']:
                    option["id"] = id
                    id = id + 1
        return Response({"data":data, "status_code": 200}, status= 200)

    def put(self, request, pk, format=None):
        workflow = self.get_object(pk)
        serializer = WorkflowSerializerPost(workflow, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "status_code":status.HTTP_201_CREATED}, status = status.HTTP_201_CREATED)
        return Response({"data":serializer.errors, "status_code": status.HTTP_400_BAD_REQUEST}, status = status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        workflow = self.get_object(pk)
        workflow.delete()
        return Response({"status_code": status.HTTP_204_NO_CONTENT}, status = status.HTTP_204_NO_CONTENT)


class ProjectList(APIView):

    def get(self, request, format=None):
        projects = Project.objects.filter(deleted=False)
        serializer = ProjectSerializer(projects, many=True)
        return Response({"data":serializer.data, "status_code": 200})

class ProjectDetail(APIView):

    def get_object(self, pk):
        try:
            return Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        project = self.get_object(pk)
        serializer = ProjectDetailSerializer(project)
        data = serializer.data
        return Response({"data":data, "status_code": 200}, status= 200)
