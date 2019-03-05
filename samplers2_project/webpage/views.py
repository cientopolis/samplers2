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
from django.core.exceptions import ObjectDoesNotExist
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


#View encargado de devolver la home con los proyectos propios o a los que fui invitado
@login_required
def home(request):
    others = request.GET.get("others")
    if others != "":
        projects_list = Project.objects.filter(
        participants__id=request.user.profile.id, deleted=False, owner=request.user.profile.user)
    else:
        projects_list = Project.objects.filter(
            participants__id=request.user.profile.id, deleted=False).exclude(owner=request.user.profile.user)
    logger.info("Returning  [%s] projects list: %s",projects_list.count(),projects_list)
    social = {}
    facebook = {}
    gmail = {}
    #Inicializo en vacio asi no se rompe la vista
    facebook['associated'] = False
    facebook['id'] = ""
    social['facebook'] = facebook
    gmail['associated'] = False
    gmail['id'] = ""
    social['gmail'] = gmail
    # Traigo las cuentas asociadas del usuario, si tiene las 2 cuentas asociadas, el primer lugar de la coleccion es facebook
    user_associateds = UserSocialAuth.objects.filter(user_id=request.user.id).order_by('provider')
    if user_associateds.count() == 1:
        if user_associateds[0].provider == "facebook":
            social['facebook']['associated'] = True
            social['facebook']['id'] = user_associateds[0].id
        else: 
            social['gmail']['associated'] = True
            social['gmail']['id'] = user_associateds[0].id
    if user_associateds.count() == 2:
        #El primero siempre es facebook porque lo trae ordenado alfabeticamente de la BD
        social['facebook']['id'] = user_associateds[0].id
        social['gmail']['id'] = user_associateds[1].id
        social['gmail']['associated'] = True
        social['facebook']['associated'] = True
    pdb.set_trace()
    context = {'projects_list': projects_list,'social':social}
    return render(request, 'webpage/home.html', context)

#View encargado de borrar un proyecto (de manera logica)
@login_required
def deleteProject(request, id=None):
    if id:
        project = get_object_or_404(Project, pk=id)
        #Si el id del usuario no coincide con un id de la lista de usuarios del proyecto, devuelvo Forbidden
        if not(project.participants.filter(pk=request.user.profile.id).exists()):
            logger.error("User id: %s hasnt permissons to perform this operation",id)
            return HttpResponseForbidden()
    else:
        project = Project(owner=request.user.profile)
    project.deleted = True
    project.save()
    logger.info("Project with id: %s deleted succesfull",id)
    messages.success(request,"Eliminacion proyecto exitoso")
    return redirect('home')

#View encargado de servir o guardar un registro de forma manual
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
            logger.info("User saved succesfull %s", user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'webpage/signup.html', {'form': form})

#Viiew encargado de crear un proyecto y guardarlo
@login_required
def createProject(request, id=None):
    project = Project()
    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user.profile.user.username
        project.save()
        #Creo un nuevo participante del proyecto como owner 
        pg = ParticipantsGroup.objects.create(project = project, profile = request.user.profile)
        pg.is_owner = True
        pg.save()
        logger.info("Project created succesfull: %s",project)
        messages.success(request, "Creacion proyecto exitoso")
        return redirect('home')
    context = {'isCreation':True}
    context['form'] = form
    return render(request, 'webpage/projectForm.html', context)

#View encargado de crear un nuevo workflow o editarlo. Este view se invoca desde la pantalla al momento de clickear en crear nuevo workflow
@login_required
def createWorkflow(request, id=None):
    project = Project.objects.get(pk=id)
    response = {}
    try:
        workflow = project.workflow
        serializer = WorkflowSerializer(workflow)
        response = serializer.data
    except ObjectDoesNotExist:
        logger.info("The project with id: %s doesnt have workflow associate",id)
        response["project"] = id
        response["steps"] = None
    response_in_json = json.dumps(response)
    ctx = { "data":response_in_json}
    return render(request, 'webpage/dashboard.html', ctx)

#View encargada de editar o servir (el form) de un proyecto
@login_required
def editProject(request, id=None):
    if id:
        project = get_object_or_404(Project, pk=id)
        #Si el id del usuario no coincide con un id de la lista de usuarios del proyecto, devuelvo Forbidden
        if not(project.participants.filter(pk=request.user.profile.id).exists()):
            logger.error("User id: %s hasnt permissons to perform this operation",id)
            return HttpResponseForbidden()
    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid():
        project = form.save()
        return redirect('home')
    context = {'isCreation':False}
    context['form'] = form
    return render(request, 'webpage/projectForm.html', context)

#View encargado de invitar a un cientifico o servir el formulario 
@login_required
def inviteScientist(request, id=None):
    if request.method == 'POST':
        if id:
            project = get_object_or_404(Project, pk=id)
            #Si el id del usuario no coincide con un id de la lista de usuarios del proyecto, devuelvo Forbidden
            if not(project.participants.filter(pk=request.user.profile.id).exists()):
                logger.error("User id: %s hasnt permissons to perform this operation",id)
                return HttpResponseForbidden()
            form = InviteScientistForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data.get('email')
                try:
                    user = User.objects.get(email = email)
                    if ParticipantsGroup.objects.filter(project=project,profile = user.profile).exists():
                        logger.error("User with id: %s is already part of this project ",id)
                        form.add_error("email", "Este cientifico ya forma parte de este proyecto")
                    else:
                        pg = ParticipantsGroup.objects.create(project = project, profile = user.profile)
                        pg.save()
                        messages.success(request,'Científico invitado exitosamente')
                        logger.info("Scientist with email : %s was invited succesfull",email)
                        return redirect('home')
                except ObjectDoesNotExist:
                    logger.info("User with email %s doesnt exist", email)
                    #send_email('Invitacion', 'Forma parte de Centopolis! Dirigete a la url y registrate :)', 'cientopolis@cientopolis.com', ['alextripero@gmail.com'])
                    form.add_error("email", "No existe un usuario con ese email. Se mandará un email para invitarlo a unirse")

    else:
        form = InviteScientistForm()
    return render(request, 'webpage/inviteScientistForm.html', {'form': form})

def send_email(message,subject,sender,receiver):
        #to = 'alexrl_lp@hotmail.com'
        #gmail_user = 'alextripero@gmail.com'
        #gmail_pwd = '****'
        #smtpserver = smtplib.SMTP("smtp.gmail.com",587)
        #smtpserver.ehlo()
        #smtpserver.starttls()
        #smtpserver.ehlo
        #smtpserver.login(gmail_user, gmail_pwd)
        #header = 'To:' + to + '\n' + 'From: ' + gmail_user + '\n' + 'Subject:testing \n'
        #msg = header + '\n this is test msg from mkyong.com \n\n'
        #smtpserver.sendmail(gmail_user, to, msg)
        #print ('done!')
        #smtpserver.close()
        send_mail(subject,message,sender,receiver,fail_silently=False)

#View encargado de mostrar los resultados del workflow
@login_required
def showResults(request, id=None):
    logger.info("Getting results for workflow with id : %s", id)
    workflow = Workflow.objects.get(id=id)
    steps_information = getStepsInformation(workflow)
    wf_results = getWfResults(workflow,request,steps_information)
    ctx = { 'steps_information': steps_information, 'wf_results' : wf_results, "wf": workflow}
    return render(request, 'webpage/showWorkflowResults.html', ctx)

#Metodo auxiliar para obtener los resultados de un workflow
def getWfResults(workflow,request,steps_information):
    wf_results = []
    media_url = request.get_host() + "/webpage" + settings.MEDIA_URL
    logger.info("Founded [%s] results for workflow", workflow.workflow_results.count())
    for wf in workflow.workflow_results.all():
        wf_result = {}
        wf_result["start_time"] = wf.start_date_time.strftime("%d-%m-%Y %H:%M:%S")
        wf_result["end_time"] = wf.end_date_time.strftime("%d-%m-%Y %H:%M:%S")
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
    return wf_results

#View encargado de descargar los resultados del workflow en csv
@login_required
def downloadCsv(request,id=None):
    workflow = Workflow.objects.get(id=id)
    logger.info("Getting Csv for workflow results of workflow with id : %s", id)
    steps_information = getStepsInformation(workflow)
    wf_results = getWfResults(workflow,request,steps_information)
    file_name = workflow.name + "_" +datetime.datetime.today().strftime('%d-%m-%Y %H:%M:%S')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="%s"' % file_name + ".csv"
    writer = csv.writer(response,delimiter=';')
    csvHeaders = getCsvHeaders(workflow)
    writer.writerow(csvHeaders) 
    writer = buildTableContent(wf_results,steps_information,writer)
    return response

def getCsvHeaders(workflow):
    result = []
    result.append("Inicio")
    result.append("Fin")
    result.append("Id")
    logger.info("Getting csv headers....")
    for step in workflow.steps.all():
        if step.step_type != StepType.INFORMATIONSTEP.value:
            result.append(step.step_type)
    return result

def buildTableContent(wf_results,steps_information,writer):
    logger.info("Building table content....")
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
    logger.info("Getting steps information")
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
    #Servicio API encargado de devolver listado de todos los workflows (no se si se usa)
    def get(self, request, format=None):
        workflows = Workflow.objects.all()
        logger.info("Founded [%s] workflows", workflows.count())
        serializer = WorkflowSerializer(Workflows, many=True)
        return Response({"data":serializer.data, "status_code": 200}, status = 200)

    #Servicio API encargado de crear un workflow (llamado desde el dashboard)
    def post(self, request, format=None):
        serializer = WorkflowSerializerPost(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info("Workflow succesfully created")
            return Response({"data": serializer.data, "status_code":status.HTTP_201_CREATED}, status=status.HTTP_201_CREATED)
        logger.error("Workflow couldnt create with errors : %s", serializer.errors)
        return Response({"data":serializer.errors, "status_code": status.HTTP_400_BAD_REQUEST}, status = status.HTTP_400_BAD_REQUEST)


class WorkflowDetail(APIView):
    
    def get_object(self, pk):
        try:
            return Workflow.objects.get(pk=pk)
        except Workflow.DoesNotExist:
            raise Http404

    #Servicio API encargado de devolver un workflow (llamado desde Samplers)
    def get(self, request, pk, format=None):
        logger.info("Getting workflow with id: %s",pk)
        workflow = self.get_object(pk)
        serializer = WorkflowSerializer(workflow)
        data = serializer.data
        return Response({"data":data, "status_code": 200}, status= 200)

    #Servicio API encargado de actualizar un workflow (llamado desde el dashboard)
    def put(self, request, pk, format=None):
        logger.info("Updating workflow with id: %s",pk)
        workflow = self.get_object(pk)
        if  workflow.workflow_results.all().count() > 0:
            logger.info("Couldnt update worfklow because this wf has already results")
            return Response({"msj":"Cant do this operation, workflow has already results"},status = 409)
        serializer = WorkflowSerializerPost(workflow, data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info("Updated wowkflow succesfully")
            return Response({"data": serializer.data, "status_code":status.HTTP_201_CREATED}, status = status.HTTP_201_CREATED)
        logger.error("The workflow could not be updated with errors : %s",serializer.errors)
        return Response({"data":serializer.errors, "status_code": status.HTTP_400_BAD_REQUEST}, status = status.HTTP_400_BAD_REQUEST)

    #Este no se si se usa
    def delete(self, request, pk, format=None):
        workflow = self.get_object(pk)
        workflow.delete()
        logger.info("Workflow with id: %s was succesfully deleted")
        return Response({"status_code": status.HTTP_204_NO_CONTENT}, status = status.HTTP_204_NO_CONTENT)


class ProjectList(APIView):
    #Servicio de API encargado de devolver tods los proyectos
    def get(self, request, format=None):
        logger.info("Getting all projects...")
        projects = Project.objects.filter(deleted=False)
        serializer = ProjectSerializer(projects, many=True)
        return Response({"data":serializer.data, "status_code": 200}, status= 200)

class ProjectDetail(APIView):

    def get_object(self, pk):
        try:
            return Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            raise Http404

    #Servicio de API encargado de devolver el detalle de un proyecto
    def get(self, request, pk, format=None):
        logger.info("Getting project detail with id: %s",pk)
        project = self.get_object(pk)
        serializer = ProjectDetailSerializer(project)
        data = serializer.data
        return Response({"data":data, "status_code": 200}, status= 200)

#Servicio encargado de postear el resultado de un workflow (se llama desde Samplers al terminar de completar los resultados del wf)
class WorkflowResult(APIView):
    
    def post(self, request, pk, format=None):
        logger.info("Saving workflow results for workflow with id: %s",pk)
        content = request.FILES['sample']
        unzipped = zipfile.ZipFile(content)
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
            logger.info("Workflow has user_id: %s", user_id)
        workflow_result.save()
        steps = data['steps']
        logger.info("The workflow result has [%s] steps",steps.count())
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
        logger.info("Workflow result was succesfully saved")
        return Response({"status_code": 200}, status= 200)

#Servicio API encargado de validar si el usuario esta logueado (se llama desde el mobile)
class Login(APIView):
    def get(self, request, format=None):
        user_id = request.GET.get("uid")
        provider = request.GET.get("provider")
        status_code = 200
        response = {}
        try:
            if provider == 'gmail':
                user_social = UserSocialAuth.objects.get(uid=user_id)
            elif provider == 'facebook': 
                user_social = UserSocialAuth.objects.get(extra_data__contains = '"token_for_business": "{}"'.format(user_id))
            else :
                status_code = 400
                response["msg"] = "Provider doesnt exist"
                return Response({"data":response, "status_code": status_code}, status= 200)
            response["msg"] = "User exists"
            response["exists"] = True
            user_information = {}
            user_information["username"] = user_social.user.username
            user_information["email"] = user_social.user.email
            user_information["id"] = user_social.user.profile.id
            response["user_information"] = user_information

        except UserSocialAuth.DoesNotExist:  
            status_code = 404
            response["msg"] = "User not exists"
            response["exists"] = False
            response["redirect_url"] = "http://localhost:8000/login/"
        return Response({"data":response, "status_code": status_code}, status= 200)

   

             

