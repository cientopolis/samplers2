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
from django.core.files import File
import datetime
from social_django.models import UserSocialAuth
from django.core.urlresolvers import reverse
from itertools import chain
import csv


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
def createWorkflow(request, id=None):
    ctx = { 'project_id':id}
    return render(request, 'webpage/dashboard.html', ctx)

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

@login_required
def showResults(request, id=None):
    if id:
        workflow = Workflow.objects.get(id=id)
    steps_information = getStepsInformation(workflow)
    wf_results = []
    media_url = request.get_host() + "/webpage" + settings.MEDIA_URL
    for wf in workflow.workflow_results.all():
        wf_result = {}
        wf_result["start_time"] = wf.start_date_time.strftime("%d-%m-%Y")
        wf_result["end_time"] = wf.end_date_time.strftime("%d-%m-%Y")
        wf_result["id"] = wf.id
        for step_information in steps_information:
            step_id = step_information['step_id'] 
            if step_information['step_type'] == StepType.TEXTSTEP.value:
                text_step_results = wf.text_step_results.all()
                if text_step_results:
                    text_step_result = text_step_results.filter(step_id=step_id).first()
                    if text_step_result:
                        wf_result[step_id] = text_step_result.inserted_text
            if step_information['step_type'] == StepType.TIMESTEP.value:
                time_step_results = wf.time_step_results.all()
                if time_step_results:
                    time_step_result = time_step_results.get(step_id=step_id)
                    if time_step_result:
                        wf_result[step_id] = time_step_result.selected_time.strftime("%H:%M:%S")
            if step_information['step_type'] == StepType.DATESTEP.value:
                date_step_results = wf.date_step_results.all()
                if date_step_results: 
                    date_step_result = date_step_results.filter(step_id=step_id).first()
                    if date_step_result:
                        wf_result[step_id] = date_step_result.selected_date.strftime("%d-%m-%Y")
            if step_information['step_type'] == StepType.LOCATIONSTEP.value:
                location_step_results = wf.location_step_results.all()
                if location_step_results:
                    location_step_result = location_step_results.filter(step_id=step_id).first()
                    if location_step_result:
                        result_location_object = {}
                        result_location_object['latitude'] = str(location_step_result.latitude)
                        result_location_object['longitude'] = str(location_step_result.longitude)
                        wf_result[step_id] = result_location_object
            if step_information['step_type'] == StepType.PHOTOSTEP.value:
                photo_step_results = wf.photo_step_results.all()
                if photo_step_results:
                    photo_step_result = photo_step_results.filter(step_id=step_id).first()
                    if photo_step_result:
                        wf_result[step_id] = media_url + str(photo_step_result.file)
            if step_information['step_type'] == StepType.SOUNDRECORDSTEP.value:
                sound_step_results = wf.sound_step_results.all()
                if sound_step_results:
                    sound_step_result = sound_step_results.get(step_id=step_id)
                    if sound_step_result:
                        wf_result[step_id] = media_url + str(sound_step_result.file)
            if step_information['step_type'] == StepType.SELECTONESTEP.value:
                one_step_results = wf.select_step_results.all().filter(type="SelectOneStepResult")
                if one_step_results:
                    one_step_result = one_step_results.filter(step_id=step_id).first()
                    if one_step_result:
                        result_options = []
                        option_results = one_step_result.options_results.all()
                        for option_result in option_results:
                            result_options.append(option_result.text_to_show)
                        wf_result[step_id] = ', '.join(result_options)
            if step_information['step_type'] == StepType.SELECTMULTIPLESTEP.value:
                multiple_step_results = wf.select_step_results.all().filter(type="SelectMultipleStepResult")
                if multiple_step_results:
                    multiple_step_result = multiple_step_results.filter(step_id=step_id).first()
                    if multiple_step_result:
                        result_options = []
                        option_results = multiple_step_result.options_results.all()
                        for option_result in option_results:
                            result_options.append(option_result.text_to_show)
                        wf_result[step_id] = ', '.join(result_options)
            '''
            Ver que hacer con el Route Step
            if step_information['step_type'] == StepType.ROUTESTEP.value:
                route_step_results = wf.route_step_results.all()
                if route_step_results:
                    route_step_result = route_step_results.filter(step_id=step_id).first()
                    if route_step_result:
                        information_route_results = route_step_result.route_information_result.first()
                        result_route_object = {}
                        
                        wf_result[step_id] = result_location_object
            '''
        wf_results.append(wf_result)

    isCsvDownload = request.GET.get('csv', None)
    if isCsvDownload:
        file_name = workflow.name + "_" +datetime.datetime.today().strftime('%d-%m-%Y %H:%M:%S')
        pdb.set_trace()
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="%s"' % file_name + ".csv"

        writer = csv.writer(response,delimiter=';')
        csvHeaders = getCsvHeaders(workflow)
        writer.writerow(csvHeaders) 
        writer = buildTableContent(wf_results,steps_information,writer)
        return response
    ctx = { 'steps_information': steps_information, 'wf_results' : wf_results, "wf_id": workflow.id}
    return render(request, 'webpage/showWorkflowResults.html', ctx)

def getCsvHeaders(workflow):
    result = []
    result.append("Inicio")
    result.append("Fin")
    result.append("Id")
    for step in workflow.steps.all():
        if step.step_type != StepType.INFORMATIONSTEP.value:
            result.append(step.step_type)
    return result

def buildTableContent(wf_results,steps_information,writer):
    for wf_result in wf_results:
        values = []
        values.append(wf_result['start_time'])
        values.append(wf_result['end_time'])
        values.append(wf_result['id'])
        for step_information in steps_information:
            id = step_information['step_id']
            if wf_result.get(id) is not None:
                values.append(wf_result[id])
            else:
                values.append("-")
        writer.writerow(values)
    return writer

def getStepsInformation(workflow):
    result = []
    for step in workflow.steps.all():
        step_information = {}
        #Elimino el information step
        if step.step_type != StepType.INFORMATIONSTEP.value:
            step_information['step_type'] = step.step_type
            step_information['step_id'] = step.step_id
            result.append(step_information)
    return result

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
        return Response({"data":serializer.data, "status_code": 200}, status= 200)

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
        unzipped.extractall('result')
        list_name = unzipped.namelist()
        for file in list_name:
            if "json" in file:
                json_file = unzipped.read(file)
        data = json.loads(json_file)
        workflow = Workflow.objects.get(id=pk)
        workflow_result = WorkflowResultModel()
        workflow_result.workflow = workflow
        workflow_result.sent = data['sent']
        workflow_result.start_date_time = dateutil.parser.parse(data['startDateTime'])
        workflow_result.end_date_time = dateutil.parser.parse(data['endDateTime'])
        custom_params = data['customParams']
        user_id = custom_params['userId']
        if user_id:
            #Chequera si es Profile.objects.get(pk=user_id) o Profile.objects.get(user=user_id)
            profile = Profile.objects.get(pk=user_id)
            workflow_result.profile = profile
        workflow_result.save()
        steps = data['steps']
        for step in steps: 
            step_type = step['type']
            step_data = step['data']
            if 'InsertTextStepResult' in step_type:
                textStepResult = TextStepResult()
                textStepResult.workflow_result = workflow_result
                textStepResult.step_id = step_data['stepId']
                textStepResult.inserted_text = step_data['insertedText']
                textStepResult.save()
            if 'LocationStepResult' in step_type:
                location_step_result = LocationStepResult()
                location_step_result.workflow_result = workflow_result
                location_step_result.step_id = step_data['stepId']
                location_step_result.latitude = step_data['latitude']
                location_step_result.longitude = step_data['longitude']
                location_step_result.save()
            if 'MultipleSelectStepResult' in step_type:
                multiple_step_result = SelectStepResult()
                multiple_step_result.workflow_result = workflow_result
                multiple_step_result.step_id = step_data['stepId']
                multiple_step_result.type = "SelectMultipleStepResult"
                multiple_step_result.save()
                options = step_data['selectedOptions']
                for option in options:
                    option_result = OptionToShowResult()
                    option_result.select_step_result = multiple_step_result
                    option_result.option_id = option['id']
                    option_result.text_to_show = option['textToShow']
                    option_result.save()
            if 'SelectOneStepResult' in step_type:
                one_step_result = SelectStepResult()
                one_step_result.workflow_result = workflow_result
                one_step_result.step_id = step_data['stepId']
                one_step_result.type = "SelectOneStepResult"
                one_step_result.save()
                option = step_data['selectedOption']
                option_result = OptionToShowResult()
                option_result.select_step_result = one_step_result
                option_result.option_id = option['id']
                option_result.text_to_show = option['textToShow']
                option_result.next_step_id = option['nextStepId']
                option_result.save()
            if 'SoundRecordStepResult' in step_type:
                record_step_result = SoundRecordStepResult()
                record_step_result.workflow_result = workflow_result
                record_step_result.step_id = step_data['stepId']
                file_name = step_data['soundFileName']
                for file in list_name:
                    if file_name in file:
                        record_file_path = unzipped.extract(file)
                record_file = open(record_file_path,'rb')
                record_step_result.file = File(record_file)
                os.remove(file_name)
                record_step_result.save()
            if 'PhotoStepResult' in step_type:
                photo_step_result = PhotoStepResult()
                photo_step_result.workflow_result = workflow_result
                photo_step_result.step_id = step_data['stepId']
                file_name = step_data['imageFileName']
                for file in list_name:
                    if file_name in file:
                        photo_file_path = unzipped.extract(file)
                photo_file = open(photo_file_path,'rb')
                photo_step_result.file = File(photo_file)
                os.remove(file_name)
                photo_step_result.save()
            if 'InsertTimeStepResult' in step_type:
                time_step_result = TimeStepResult()
                time_step_result.workflow_result = workflow_result
                time_step_result.step_id = step_data['stepId']
                time_step_result.selected_time = dateutil.parser.parse(step_data['selected_time'])
                time_step_result.save()
            if 'InsertDateStepResult' in step_type:
                date_step_result = DateStepResult()
                date_step_result.workflow_result = workflow_result
                date_step_result.step_id = step_data['stepId']
                date_step_result.selected_date = dateutil.parser.parse(step_data['selected_time'])
                date_step_result.save()
            if 'RouteStepResult' in step_type:
                route_step_result = RouteStepResult()
                route_step_result.workflow_result = workflow_result
                route_step_result.step_id = step_data['stepId']
                route_step_result.save()
                routes = step_data['route']
                for route in routes:
                    route_information_result = RouteInformationResult()
                    route_information_result.route_step_result = route_step_result
                    route_information_result.accuracy = route['mAccuracy']
                    route_information_result.altitude = route['mAltitude']
                    route_information_result.bearing = route['mBearing']
                    route_information_result.elapsed_realtime_nanos = route['mElapsedRealtimeNanos']
                    route_information_result.latitude = route['mLatitude']
                    route_information_result.longitude = route['mLongitude']
                    route_information_result.provider = route['mProvider']
                    route_information_result.speed = route['mSpeed']
                    route_information_result.fields_mask = route['mFieldsMask']
                    route_information_result.time = datetime.datetime.fromtimestamp(route['mTime'] / 1e3)
                    #Si tiene extras
                    extra = route['mExtras']
                    if not extra is None:
                        route_information_result.flags = extra['mFlags']
                        #Si tiene parcelledData
                        parcelledData = extra['mParcelledData']
                        if not parcelledData is None:
                            route_information_result.native_ptr = parcelledData['mNativePtr']
                            route_information_result.native_size = parcelledData['mNativeSize']
                            route_information_result.owns_native_parcel_object = parcelledData['mOwnsNativeParcelObject']
                    route_information_result.save()

        return Response({"status_code": 200}, status= 200)


class Prueba(APIView):
    def get(self, request, format=None):
        zip_file = os.path.join(settings.PROJECT_ROOT, 'sample2 |.zip')
        unzipped = zipfile.ZipFile(zip_file)
        unzipped.extractall('result')
        list_name = unzipped.namelist()
        for file in list_name:
            if "json" in file:
                json_file = unzipped.read(file)
        data = json.loads(json_file)
        workflow = Workflow.objects.get(id=1)
        workflow_result = WorkflowResultModel()
        workflow_result.workflow = workflow
        workflow_result.sent = data['sent']
        workflow_result.start_date_time = dateutil.parser.parse(data['startDateTime'])
        workflow_result.end_date_time = dateutil.parser.parse(data['endDateTime'])
        workflow_result.save()
        steps = data['steps']
        for step in steps: 
            step_type = step['type']
            if  step_type == StepType.TEXTSTEP.value:
                textStepResult = TextStepResult()
                textStepResult.workflow_result = workflow_result
                textStepResult.step_id = step['stepId']
                textStepResult.inserted_text = step['insertedText']
                textStepResult.save()
            if step_type == StepType.LOCATIONSTEP.value:
                location_step_result = LocationStepResult()
                location_step_result.workflow_result = workflow_result
                location_step_result.step_id = step['stepId']
                location_step_result.latitude = step['latitude']
                location_step_result.longitude = step['longitude']
                location_step_result.save()
            if step_type == StepType.SELECTMULTIPLESTEP.value:
                multiple_step_result = SelectStepResult()
                multiple_step_result.workflow_result = workflow_result
                multiple_step_result.step_id = step['stepId']
                multiple_step_result.type = "SelectMultipleStepResult"
                multiple_step_result.save()
                options = step['selectedOptions']
                for option in options:
                    option_result = OptionToShowResult()
                    option_result.select_step_result = multiple_step_result
                    option_result.option_id = option['id']
                    option_result.text_to_show = option['textToShow']
                    option_result.save()
            if step_type == StepType.SELECTONESTEP.value:
                one_step_result = SelectStepResult()
                one_step_result.workflow_result = workflow_result
                one_step_result.step_id = step['stepId']
                one_step_result.type = "SelectOneStepResult"
                one_step_result.save()
                option = step['selectedOption']
                option_result = OptionToShowResult()
                option_result.select_step_result = one_step_result
                option_result.option_id = option['id']
                option_result.text_to_show = option['textToShow']
                option_result.next_step_id = option['nextStepId']
                option_result.save()
            if step_type == StepType.SOUNDRECORDSTEP.value:
                record_step_result = SoundRecordStepResult()
                record_step_result.workflow_result = workflow_result
                record_step_result.step_id = step['stepId']
                file_name = step['soundFileName']
                for file in list_name:
                    if file_name in file:
                        record_file_path = unzipped.extract(file)
                record_file = open(record_file_path,'rb')
                record_step_result.file = File(record_file)
                os.remove(file_name)
                record_step_result.save()
            if step_type == StepType.PHOTOSTEP.value:
                photo_step_result = PhotoStepResult()
                photo_step_result.workflow_result = workflow_result
                photo_step_result.step_id = step['stepId']
                file_name = step['imageFileName']
                for file in list_name:
                    if file_name in file:
                        photo_file_path = unzipped.extract(file)
                photo_file = open(photo_file_path,'rb')
                photo_step_result.file = File(photo_file)
                os.remove(file_name)
                photo_step_result.save()
            if step_type == StepType.TIMESTEP.value:
                time_step_result = TimeStepResult()
                time_step_result.workflow_result = workflow_result
                time_step_result.step_id = step['stepId']
                time_step_result.selected_time = dateutil.parser.parse(step['selected_time'])
                time_step_result.save()
            if step_type == StepType.DATESTEP.value:
                date_step_result = DateStepResult()
                date_step_result.workflow_result = workflow_result
                date_step_result.step_id = step['stepId']
                date_step_result.selected_date = dateutil.parser.parse(step['selected_date'])
                date_step_result.save()
            if step_type == StepType.ROUTESTEP.value:
                route_step_result = RouteStepResult()
                route_step_result.workflow_result = workflow_result
                route_step_result.step_id = step['stepId']
                route_step_result.save()
                routes = step['route']
                for route in routes:
                    route_information_result = RouteInformationResult()
                    route_information_result.route_step_result = route_step_result
                    route_information_result.accuracy = route['mAccuracy']
                    route_information_result.altitude = route['mAltitude']
                    route_information_result.bearing = route['mBearing']
                    route_information_result.elapsed_realtime_nanos = route['mElapsedRealtimeNanos']
                    route_information_result.latitude = route['mLatitude']
                    route_information_result.longitude = route['mLongitude']
                    route_information_result.provider = route['mProvider']
                    route_information_result.speed = route['mSpeed']
                    route_information_result.fields_mask = route['mFieldsMask']
                    route_information_result.time = datetime.datetime.fromtimestamp(route['mTime'] / 1e3)
                    #Si tiene extras
                    extra = route['mExtras']
                    if not extra is None:
                        route_information_result.flags = extra['mFlags']
                        #Si tiene parcelledData
                        parcelledData = extra['mParcelledData']
                        if not parcelledData is None:
                            route_information_result.native_ptr = parcelledData['mNativePtr']
                            route_information_result.native_size = parcelledData['mNativeSize']
                            route_information_result.owns_native_parcel_object = parcelledData['mOwnsNativeParcelObject']
                    route_information_result.save() 

class Login(APIView):
    def get(self, request, format=None):
        user_id = request.GET.get("uid")
        provider = request.GET.get("provider")
        status_code = 200
        obj = {}
        obj["msg"] = "User exists"
        obj["exists"] = True
        try:
            user_social = UserSocialAuth.objects.get(uid=user_id)
            user_information = {}
            user_information["username"] = user_social.user.username
            user_information["email"] = user_social.user.email
            user_information["id"] = user_social.user.profile.id
            obj["user_information"] = user_information

        except UserSocialAuth.DoesNotExist:  
            status_code = 404
            obj["msg"] = "User not exists"
            obj["exists"] = False
            obj["redirect_url"] = "http://localhost:8000/login/"
        return Response({"data":obj, "status_code": status_code}, status= 200)

    '''
    def post(self, request, format=None):
        serializer = UserSocialAuthSerializer(data=request.data)
        if serializer.is_valid():
            new_user = User()
            username = serializer.validated_data['extra_data']['username']
            email = serializer.validated_data['extra_data']['email']
            new_user.username = username
            new_user.email = email
            new_user.save() 
            pdb.set_trace()
            serializer.validated_data['user_id'] = new_user.id
            serializer.save()
            return Response({"data": serializer.data, "status_code":status.HTTP_201_CREATED}, status=status.HTTP_201_CREATED)
        return Response({"data":serializer.errors, "status_code": status.HTTP_400_BAD_REQUEST}, status = status.HTTP_400_BAD_REQUEST)
    '''

             

