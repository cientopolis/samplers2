from django.contrib import admin
from webpage.models import Profile
from webpage.models import Project
from webpage.models import Workflow
from webpage.models import Step
from webpage.models import DateStep
from webpage.models import TextStep
from webpage.models import InformationStep
from webpage.models import PhotoStep
from webpage.models import LocationStep
from webpage.models import MultipleSelectStep
from webpage.models import MultipleSelectOption
from webpage.models import SelectOneStep
from webpage.models import SelectOneOption

admin.site.register(Project)
admin.site.register(Profile)
admin.site.register(Workflow)
admin.site.register(Step)
admin.site.register(DateStep)
admin.site.register(TextStep)
admin.site.register(InformationStep)
admin.site.register(PhotoStep)
admin.site.register(LocationStep)
admin.site.register(MultipleSelectStep)
admin.site.register(MultipleSelectOption)
admin.site.register(SelectOneStep)
admin.site.register(SelectOneOption)


