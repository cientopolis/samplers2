from django.contrib import admin
from webpage.models import Profile
from webpage.models import Project
from webpage.models import Workflow
from webpage.models import Step
from webpage.models import OptionToShow

admin.site.register(Project)
admin.site.register(Profile)
admin.site.register(Workflow)
admin.site.register(Step)
admin.site.register(OptionToShow)



