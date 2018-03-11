from django.contrib import admin
from django.contrib.auth.models import User
from webpage.models import Profile
from webpage.models import Project
from webpage.models import Workflow
from webpage.models import Step
from webpage.models import OptionToShow
from webpage.models import ParticipantsGroup


class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'email',
                    'first_name', 'last_name', 'last_login', 'is_staff']

class ParticipantsGroupInline(admin.TabularInline):
    model = ParticipantsGroup
    extra = 1

class ProfileAdmin(admin.ModelAdmin):
    inlines = (ParticipantsGroupInline,)
    list_display = ['id', 'id_user', 'facebook_username',
                    'gmail_username', 'gender', 'bio', 'location', 'institucion']

    def id_user(self, instance):
        return instance.user.id

class ParticipantsGroupAdmin(admin.ModelAdmin):
    list_display = ['profile', 'project', 'is_owner']



class ProjectAdmin(admin.ModelAdmin):
    inlines = (ParticipantsGroupInline,)
    list_display = ['id', 'name', 'deleted']

    #def id_owner(self, instance):
        #return instance.owner.id

class WorkflowAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'id_project']

    def id_project(sel, instance):
        return instance.project.id


class StepAdmin(admin.ModelAdmin):
    list_display = ['id', 'step_type', 'order_in_workflow', 'id_workflow', 'text_to_show',
                    'sample_test', 'max_length', 'input_type', 'optional', 'instruct_to_show', 'image_to_overlay', 'title']

    def id_workflow(self, instance):
        return instance.workflow.id


class OptionToShowAdmin(admin.ModelAdmin):
    list_display = ['id', 'text_to_show', 'id_step', 'order_in_steps']

    def id_step(self, instance):
        return instance.step.id


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Workflow, WorkflowAdmin)
admin.site.register(Step, StepAdmin)
admin.site.register(OptionToShow, OptionToShowAdmin)
admin.site.register(ParticipantsGroup, ParticipantsGroupAdmin)
