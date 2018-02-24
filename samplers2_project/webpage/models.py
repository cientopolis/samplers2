from django.db import models
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

@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

class Project(models.Model):
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE) 
    name = models.CharField(max_length=30, blank=True)
    #Description, fecha de la creacion, hitos,worlflow_id
    deleted = models.BooleanField(default=False)
    def __str__(self):
        return self.name

#class Hito
class Workflow(models.Model):
    name = models.CharField(max_length=30, blank=True)

class Step(models.Model):
    step_type = models.CharField(max_length=30, blank=True)
    #Ver si van estos
    # identifier = models.IntegerField()
    # next_step = models.IntegerField()
    order_in_workflow = models.IntegerField(null = True)
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE)
    text_to_show = models.TextField(max_length=500, blank=True)
    #Only for TextStep
    sample_test = models.TextField(max_length=500, blank=True)
    max_length = models.IntegerField()
    optional = models.BooleanField(default=False)
    #Only for PhotoStep
    instruct_to_show = models.TextField(max_length=500, blank=True)
    image_to_overlay = models.TextField(max_length=500, blank=True)
    #Ver si va esto
    #INPUT_TYPE = (
    #   ('N', 'number'),
    #   ('M', 'text'),
    #   ('L', 'decimal'),
    #)
    #inputy_type = models.CharField(max_length=1,choices=INPUT_TYPE)
    #Ony for SelectOneOptionStep and MultipleOptionStep
    title = models.TextField(max_length=500, blank=True)


#class DateStep(models.Model):
    #step = models.ForeignKey(Step, on_delete=models.CASCADE)
    #text_to_show = models.TextField(max_length=500, blank=True)

#class TextStep(models.Model):
    #step = models.ForeignKey(Step, on_delete=models.CASCADE)
    #text_to_show = models.TextField(max_length=500, blank=True)
    #sample_test = models.TextField(max_length=500, blank=True)
    #max_length = models.IntegerField()
    #Ver si guardar esto
    #INPUT_TYPE = (
    #   ('N', 'number'),
    #   ('M', 'text'),
    #   ('L', 'decimal'),
    #)
    #inputy_type = models.CharField(max_length=1,choices=INPUT_TYPE)
    #optional = models.BooleanField(default=False)

#class InformationStep(models.Model):
    #step = models.ForeignKey(Step, on_delete=models.CASCADE)
    #text_to_show = models.TextField(max_length=500, blank=True)

#class PhotoStep(models.Model):
    #step = models.ForeignKey(Step, on_delete=models.CASCADE)
    #instruct_to_show = models.TextField(max_length=500, blank=True)
    #image_to_overlay = models.TextField(max_length=500, blank=True)

#class LocationStep(models.Model):
    #step = models.ForeignKey(Step, on_delete=models.CASCADE)
    #text_to_show = models.TextField(max_length=500, blank=True)

#class SelectMultipleStep(models.Model):
    #step = models.ForeignKey(Step, on_delete=models.CASCADE)
    #title = models.TextField(max_length=500, blank=True)

class OptionToShow(models.Model):
    text_to_show = models.TextField(max_length=500, blank=True)
    step = models.ForeignKey(Step, on_delete=models.CASCADE)
    order_in_steps = models.IntegerField(null = True)


#class SelectOneStep(models.Model):
    #step = models.ForeignKey(Step, on_delete=models.CASCADE)
    #title = models.TextField(max_length=500, blank=True)

#class SelectOneOption(models.Model):
    #text_to_show = models.TextField(max_length=500, blank=True)
    #step = models.ForeignKey(Step, on_delete=models.CASCADE)
    #order_in_steps = models.IntegerField(null = True)







