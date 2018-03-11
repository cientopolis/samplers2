from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.forms import ModelForm

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
    #owner = models.ForeignKey(Profile, on_delete=models.CASCADE)
    participants = models.ManyToManyField(Profile, through='ParticipantsGroup') 
    name = models.CharField(max_length=30, blank=True)
    #Description, fecha de la creacion, hitos,worlflow_id
    deleted = models.BooleanField(default=False)
    def __str__(self):
        return self.name

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
        ("TimeStep" , "TimeStep")
    )
    step_type = models.CharField(max_length=30, choices = STEP_CHOICES, null = False)
    #Ver si van estos
    # identifier = models.IntegerField()
    # next_step = models.IntegerField()
    order_in_workflow = models.IntegerField()
    workflow = models.ForeignKey(Workflow, related_name='steps', on_delete=models.CASCADE)
    text_to_show = models.TextField(max_length=500, blank=True)
    #Only for TextStep
    sample_test = models.TextField(max_length=500, blank=True)
    max_length = models.IntegerField(null = True, blank=True)
    optional = models.NullBooleanField(blank=True, null=True,)
    #Ver si va esto
    INPUT_TYPE = (
       ('number', 'number'),
       ('text', 'text'),
       ('decimal', 'decimal'),
    )
    input_type = models.CharField(max_length=1,choices=INPUT_TYPE, blank= True)
    #Only for PhotoStep
    instruct_to_show = models.TextField(max_length=500, blank=True)
    image_to_overlay = models.TextField(max_length=500, blank=True)
    #Ony for SelectOneOptionStep and MultipleOptionStep
    title = models.TextField(max_length=500, blank=True)
    def __str__(self):
        return str(self.id)

class OptionToShow(models.Model):
    text_to_show = models.TextField(max_length=500, blank=True)
    step = models.ForeignKey(Step, related_name = "options_to_show", on_delete=models.CASCADE)
    order_in_steps = models.IntegerField()
