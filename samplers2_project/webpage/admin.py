from django.contrib import admin
from django.contrib.auth.models import User
from webpage.models import *
import pdb


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
    list_display = ['id', 'name', 'description','owner','deleted','created_date']

    #def id_owner(self, instance):
        #return instance.owner.id

class WorkflowAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'id_project']

    def id_project(sel, instance):
        return instance.project.id


class StepAdmin(admin.ModelAdmin):
    list_display = ['id', 'step_type', 'next_step_id', 'order_in_workflow', 'id_workflow', 'text_to_show',
                    'sample_text', 'max_length', 'input_type', 'optional']

    def id_workflow(self, instance):
        return instance.workflow.id


class OptionToShowAdmin(admin.ModelAdmin):
    list_display = ['id', 'text_to_show', 'id_step', 'order_in_steps','next_step_id']

    def id_step(self, instance):
        return instance.step.id

class WorkflowResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'id_workflow', 'id_start_date_time', 'id_end_date_time', 'sent']

    def id_start_date_time(self, instance):
        return instance.start_date_time.strftime("%d %b %Y %H:%M:%S")
    id_start_date_time.admin_order_field = 'start_date_time'
    id_start_date_time.short_description = 'Start Date Time'

    def id_workflow(self, instance):
        return instance.workflow.id

    def id_end_date_time(self, instance):
        return instance.end_date_time.strftime("%d %b %Y %H:%M:%S")
    id_end_date_time.admin_order_field = 'end_date_time'
    id_end_date_time.short_description = 'End Date Time'

class TextStepResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'id_workflow_result', 'step_id', 'inserted_text']

    def id_workflow_result(self, instance):
        return instance.workflow_result.id

class LocationStepResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'id_workflow_result', 'step_id', 'latitude', 'longitude']

    def id_workflow_result(self, instance):
        return instance.workflow_result.id

class SelectStepResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'id_workflow_result', 'step_id', 'type']

    def id_workflow_result(self, instance):
        return instance.workflow_result.id

class OptionToShowResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'id_select_step_result', 'text_to_show','option_id','next_step_id']

    def id_select_step_result(self, instance):
        return instance.select_step_result.id

class SoundRecordStepResultAdmin(admin.ModelAdmin):
    list_display = ['id','id_workflow_result', 'step_id','file']

    def id_workflow_result(self, instance):
        return instance.workflow_result.id

class PhotoStepResultAdmin(admin.ModelAdmin):
    list_display = ['id','id_workflow_result', 'step_id','file']

    def id_workflow_result(self, instance):
        return instance.workflow_result.id

class TimeStepResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'id_workflow_result', 'id_selected_time']

    def id_workflow_result(self, instance):
        return instance.workflow_result.id

    def id_selected_time(self, instance):
        return instance.selected_time.strftime("%d %b %Y %H:%M:%S")
    id_selected_time.admin_order_field = 'selected_date_time'
    id_selected_time.short_description = 'Selected Date Time'

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Workflow, WorkflowAdmin)
admin.site.register(Step, StepAdmin)
admin.site.register(OptionToShow, OptionToShowAdmin)
admin.site.register(ParticipantsGroup, ParticipantsGroupAdmin)
admin.site.register(WorkflowResult, WorkflowResultAdmin)
admin.site.register(TextStepResult, TextStepResultAdmin)
admin.site.register(LocationStepResult, LocationStepResultAdmin)
admin.site.register(SelectStepResult, SelectStepResultAdmin)
admin.site.register(OptionToShowResult, OptionToShowResultAdmin)
admin.site.register(SoundRecordStepResult, SoundRecordStepResultAdmin)
admin.site.register(PhotoStepResult, PhotoStepResultAdmin)
admin.site.register(TimeStepResult, TimeStepResultAdmin)
