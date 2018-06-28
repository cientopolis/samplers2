from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from webpage.forms import SignUpForm, ProjectForm, InviteScientistForm
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from webpage.models import *
from webpage.models import WorkflowResult as WorkflowResultModel
from webpage.serializers import *
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib import messages 
import zipfile
import pdb
from django.conf import settings
import os
from json import JSONDecoder
from functools import partial
from webpage.enums import StepType
import dateutil.parser
import json


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
    if request.method == 'POST':
        if id:
            project = get_object_or_404(Project, pk=id)
            #Si el id del usuario no coincide con un id de la lista de usuarios del proyecto, devuelvo Forbidden
            if not(project.participants.filter(pk=request.user.profile.id).exists()):
                return HttpResponseForbidden()
            form = InviteScientistForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data.get('email')
                user = User.objects.get(email = email)
                if ParticipantsGroup.objects.filter(project=project,profile = user.profile).exists():
                    messages.error(request, "Este cientifico ya forma parte de este proyecto")
                else:
                    pg = ParticipantsGroup.objects.create(project = project, profile = user.profile)
                    pg.save()
                    return redirect('home')
    else:
        form = InviteScientistForm()
    return render(request, 'webpage/inviteScientistForm.html', {'form': form})


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
        for index, obj in enumerate(data['steps'],start=1):
            obj["id"] = index
            if (obj['step_type'] == StepType.SELECTONESTEP.value) | (obj['step_type'] == StepType.SELECTMULTIPLESTEP.value):
                for idx, option in enumerate(obj['options_to_show'],start =1):
                    option["id"] = idx
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


class WorkflowResult(APIView):
    """
    List all workflow, or create a new workflow.
    """
    def post(self, request, pk, format=None):
        content = request.FILES['sample']
        unzipped = zipfile.ZipFile(content)
        unzipped.extractall("tmp")
        list = unzipped.namelist()
        for file in list:
            filecontent = unzipped.read(file)
            pdb.set_trace()

class Prueba(APIView):
    def get(self, request, format=None):
        workflow = Workflow.objects.get(id=33)
        workflow_result = WorkflowResultModel()
        #file2 = open(os.path.join(settings.PROJECT_ROOT, 'sample_1529373823048.json'))
        zip_file = os.path.join(settings.PROJECT_ROOT, 'sample.zip')
        unzipped = zipfile.ZipFile(zip_file)
        list_name = unzipped.namelist()
        for file in list_name:
            if "json" in file:
                json_file = unzipped.read(file)
                
        data = json.loads(json_file)
        workflow_result.workflow = workflow
        workflow_result.sent = data['sent']
        workflow_result.start_date_time = dateutil.parser.parse(data['startDateTime'])
        workflow_result.end_date_time = dateutil.parser.parse(data['endDateTime'])
        workflow_result.save()
        steps = data['steps']
        for step in steps: 
            if step['type'] == StepType.TEXTSTEP.value:
                textStepResult = TextStepResult()
                textStepResult.workflow_result = workflow_result
                textStepResult.step_id = step['stepId']
                textStepResult.inserted_text = step['insertedText']
                textStepResult.save()
            if step['type'] == StepType.LOCATIONSTEP.value:
                location_step_result = LocationStepResult()
                location_step_result.workflow_result = workflow_result
                location_step_result.step_id = step['stepId']
                pdb.set_trace()
                location_step_result.latitude = step['latitude']
                location_step_result.longitude = step['longitude']
                pdb.set_trace()
                location_step_result.save()                    

