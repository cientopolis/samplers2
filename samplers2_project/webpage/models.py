from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.forms import ModelForm
from django.utils import timezone
import pdb

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    facebook_username =  models.CharField(max_length=255, blank=True)
    gmail_username =  models.CharField(max_length=255, blank=True)
    gender = models.CharField(max_length=40, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    institucion = models.CharField(max_length=30, blank=True)
    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

class Project(models.Model):
    owner = models.TextField(max_length=100, blank=True)
    participants = models.ManyToManyField(Profile, through='ParticipantsGroup') 
    name = models.CharField(max_length=30, blank=True)
    description = models.TextField(max_length=500, blank=True)
    #Description, fecha de la creacion, hitos,worlflow_id
    deleted = models.BooleanField(default=False)
    created_date = models.DateTimeField(editable=False)
    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created_date = timezone.now()
        return super(Project, self).save(*args, **kwargs)

class ParticipantsGroup(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    is_owner = models.BooleanField(default=False)

    
#class Hito
class Workflow(models.Model):
    project = models.OneToOneField(Project, related_name= 'workflow', on_delete=models.CASCADE)
    name = models.CharField(max_length=30, blank=True)
    def __str__(self):
        return self.name

class Step(models.Model):
    STEP_CHOICES = (
        ("DateStep" ,"DateStep"),
        ("TextStep" ,"TextStep"),
        ("InformationStep" , "InformationStep"),
        ("PhotoStep" , "PhotoStep"),
        ("LocationStep" , "LocationStep"),
        ("SelectOneStep" , "SelectOneStep"),
        ("SelectMultipleStep" , "SelectMultipleStep"),
        ("TimeStep" , "TimeStep"),
        ("RouteStep", "RouteStep"),
        ("SoundRecordStep", "SoundRecordStep")
    )
    step_type = models.CharField(max_length=30, choices = STEP_CHOICES, null = False)
    #Ver si van estos
    # identifier = models.IntegerField()
    next_step_id = models.IntegerField(null = True, blank=True)
    step_id = models.IntegerField(null=False)
    workflow = models.ForeignKey(Workflow, related_name='steps', on_delete=models.CASCADE)
    text_to_show = models.TextField(max_length=500, blank=True)
    #Only for TextStep
    sample_text = models.TextField(max_length=500, blank=True)
    max_length = models.IntegerField(null = True, blank=True)
    optional = models.NullBooleanField(blank=True, null=True)
    #Ver si va esto
    INPUT_TYPE = (
       ('number', 'number'),
       ('text', 'text'),
       ('decimal', 'decimal'),
    )
    input_type = models.CharField(max_length=1,choices=INPUT_TYPE, blank= True)
    #Only for SelectOneOptionStep and MultipleOptionStep
    title = models.TextField(max_length=500, blank=True)
    def __str__(self):
        return str(self.id)

class OptionToShow(models.Model):
    text_to_show = models.TextField(max_length=500, blank=True)
    step = models.ForeignKey(Step, related_name = "options_to_show", on_delete=models.CASCADE)
    option_id = models.IntegerField()
    next_step_id = models.IntegerField(null = True, blank=True)

class WorkflowResult(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null = True)
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE,related_name = "workflow_results")
    start_date_time = models.DateTimeField(blank=True, null=True)
    end_date_time = models.DateTimeField(blank=True, null=True)
    sent = models.NullBooleanField(blank=True, null=True)

class TextStepResult(models.Model):
    workflow_result = models.ForeignKey(WorkflowResult, on_delete=models.CASCADE,related_name = "text_step_results")
    step_id = models.IntegerField(null = True, blank=True)
    inserted_text = models.TextField(max_length=500, blank=True)

class TimeStepResult(models.Model):
    workflow_result = models.ForeignKey(WorkflowResult, on_delete=models.CASCADE,related_name = "time_step_results")
    step_id = models.IntegerField(null = True, blank=True)
    selected_time = models.DateTimeField()

class DateStepResult(models.Model):
    workflow_result = models.ForeignKey(WorkflowResult, on_delete=models.CASCADE,related_name = "date_step_results")
    step_id = models.IntegerField(null = True, blank=True)
    selected_date = models.DateTimeField()

def workflow_result_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/workflow_result_<id>/<filename>
    name = filename.split("/")[-1]
    return 'workflow_result_{0}/{1}'.format(instance.workflow_result.id, name)

class SoundRecordStepResult(models.Model):
    workflow_result = models.ForeignKey(WorkflowResult, on_delete=models.CASCADE,related_name = "sound_step_results")
    step_id = models.IntegerField(null = True, blank=True)
    file = models.FileField(blank=False, null=False, upload_to=workflow_result_directory_path)

class PhotoStepResult(models.Model):
    workflow_result = models.ForeignKey(WorkflowResult, on_delete=models.CASCADE,related_name = "photo_step_results")
    step_id = models.IntegerField(null = True, blank=True)
    file = models.ImageField(blank=False, null=False, upload_to=workflow_result_directory_path)

class SelectStepResult(models.Model):
    workflow_result = models.ForeignKey(WorkflowResult, on_delete=models.CASCADE,related_name = "select_step_results")
    step_id = models.IntegerField(null = True, blank=True)
    TYPE_CHOICES = (
        ("SelectOneStepResult" , "SelectOneStepResult"),
        ("SelectMultipleStepResult" , "SelectMultipleStepResult"),
        
    )
    type = models.CharField(max_length=30, choices = TYPE_CHOICES, null = False)

class OptionToShowResult(models.Model):
    select_step_result = models.ForeignKey(SelectStepResult, on_delete=models.CASCADE,related_name = "options_results")
    text_to_show = models.TextField(max_length=500, blank=True)
    option_id = models.IntegerField(null = True, blank=True)
    next_step_id = models.IntegerField(null = True, blank=True)

class LocationStepResult(models.Model):
    workflow_result = models.ForeignKey(WorkflowResult, on_delete=models.CASCADE,related_name = "location_step_results")
    step_id = models.IntegerField(null = True, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)

class RouteStepResult(models.Model):
    workflow_result = models.ForeignKey(WorkflowResult, on_delete=models.CASCADE,related_name = "route_step_results")
    step_id = models.IntegerField(null = True, blank=True)

class RouteInformationResult(models.Model):
    route_step_result = models.ForeignKey(RouteStepResult, on_delete=models.CASCADE,related_name = "route_information_results")
    accuracy = models.DecimalField(max_digits=10, decimal_places=4)
    altitude = models.DecimalField(max_digits=10, decimal_places=4)
    bearing = models.DecimalField(max_digits=10, decimal_places=4)
    elapsed_realtime_nanos = models.BigIntegerField()
    fields_mask = models.IntegerField()
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    provider = models.TextField(max_length=500)
    speed = models.IntegerField()
    time = models.DateTimeField()
    #Empieza el objeto mExtras, ver si moderlarlo todo aca
    flags = models.IntegerField(null = True, blank=True)
    #Empieza el objeto parcelledData dentro de mExtras, ver si modelarlo aca
    native_ptr = models.BigIntegerField(null = True, blank=True)
    native_size = models.IntegerField(null = True, blank=True)
    owns_native_parcel_object = models.NullBooleanField(blank=True, null=True)

