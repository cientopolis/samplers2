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
    order_in_workflow = models.IntegerField(null = True)
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE)

class DateStep(models.Model):
    step = models.ForeignKey(Step, on_delete=models.CASCADE)
    text_to_show = models.TextField(max_length=500, blank=True)

class TextStep(models.Model):
    step = models.ForeignKey(Step, on_delete=models.CASCADE)
    text_to_show = models.TextField(max_length=500, blank=True)
    sample_test = models.TextField(max_length=500, blank=True)
    max_length = models.IntegerField()
    INPUT_TYPE = (
        ('N', 'number'),
        ('M', 'text'),
        ('L', 'decimal'),
    )
    inputy_type = models.CharField(max_length=1,choices=INPUT_TYPE)
    optional = models.BooleanField(default=False)

class InformationStep(models.Model):
    step = models.ForeignKey(Step, on_delete=models.CASCADE)
    text_to_show = models.TextField(max_length=500, blank=True)

class PhotoStep(models.Model):
    step = models.ForeignKey(Step, on_delete=models.CASCADE)
    instruct_to_show = models.TextField(max_length=500, blank=True)
    image_to_overlay = models.TextField(max_length=500, blank=True)

class LocationStep(models.Model):
    step = models.ForeignKey(Step, on_delete=models.CASCADE)
    text_to_show = models.TextField(max_length=500, blank=True)

class MultipleSelectStep(models.Model):
    step = models.ForeignKey(Step, on_delete=models.CASCADE)
    text_to_show = models.TextField(max_length=500, blank=True)

class MultipleSelectOption(models.Model):
    text_to_show = models.TextField(max_length=500, blank=True)
    step = models.ForeignKey(MultipleSelectStep, on_delete=models.CASCADE)

class SelectOneStep(models.Model):
    step = models.ForeignKey(Step, on_delete=models.CASCADE)
    title = models.TextField(max_length=500, blank=True)

class SelectOneOption(models.Model):
    text_to_show = models.TextField(max_length=500, blank=True)
    step = models.ForeignKey(SelectOneStep, on_delete=models.CASCADE)






