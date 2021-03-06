from rest_framework import serializers
from webpage.models import OptionToShow, Step, Workflow, Project
from webpage.enums import StepType
from social_django.models import UserSocialAuth
from rest_framework import serializers
import pdb


class OptionToShowSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='option_id')
    class Meta:
        model = OptionToShow
        fields = ('text_to_show','next_step_id','id')
        
    def to_representation(self, obj):
        ret = super(OptionToShowSerializer, self).to_representation(obj)         
        if (obj.step.step_type != StepType.SELECTONESTEP.value):
            ret.pop('next_step_id')
        return ret


class StepSerializer (serializers.ModelSerializer):
    id = serializers.SerializerMethodField('get_step_id_name')
    class Meta:
        model = Step
        fields = ('step_type', 'next_step_id', 'id', 'text_to_show', 'sample_text', 'max_length', 'optional',
                  'title', 'options_to_show')

    def to_representation(self, obj):
        ret = super(StepSerializer, self).to_representation(obj)          
        if obj.step_type != StepType.TEXTSTEP.value:
            ret.pop('sample_text')
            ret.pop('max_length')
            ret.pop('optional')
        if (obj.step_type != StepType.SELECTONESTEP.value) & (obj.step_type != StepType.SELECTMULTIPLESTEP.value):
            ret.pop('title')
            ret.pop('options_to_show')  
        return ret
    options_to_show = serializers.SerializerMethodField()

    def get_step_id_name(self,obj):
        return obj.step_id

    def get_options_to_show(self, instance):
        options_to_show = instance.options_to_show.all().order_by('option_id')
        return OptionToShowSerializer(options_to_show, many=True).data



class StepSerializerPost (serializers.ModelSerializer):
    options_to_show = OptionToShowSerializer(many=True, required=False)
    id = id = serializers.CharField(source='step_id')
    class Meta:
        model = Step
        fields = ('step_type', 'next_step_id','id','text_to_show', 'sample_text', 'max_length', 'input_type', 'optional',
                  'title', 'options_to_show')
        #read_only_fields = ('next_step_id',)


class WorkflowSerializer(serializers.ModelSerializer):
    steps = serializers.SerializerMethodField()

    class Meta:
        model = Workflow
        fields = ('id','name', 'project', 'steps')

    def get_steps(self, instance):
        steps = instance.steps.all().order_by('step_id')
        return StepSerializer(steps, many=True).data


class WorkflowSerializerPost(serializers.ModelSerializer):
    steps = StepSerializerPost(many=True)

    class Meta:
        model = Workflow
        fields = ('name', 'project', 'steps')

    def create(self, validated_data):
        steps_data = validated_data.pop('steps')
        workflow = Workflow.objects.create(**validated_data)
        createWorkflowWithSteps(steps_data, workflow)
        return workflow

    def update(self, instance, validated_data):
        workflow = Workflow.objects.get(id= instance.id)
        workflow.delete()
        steps_data = validated_data.pop('steps')
        workflow = Workflow.objects.create(id=instance.id,**validated_data)
        createWorkflowWithSteps(steps_data, workflow)
        return instance

def createWorkflowWithSteps(steps, workflow):
        for index, step in enumerate(steps):
            step_dictionary = steps[index]
            step_type = step_dictionary['step_type']
            options_to_show_data = []
            # Si es de estos tipos, saco los options_to_show para desp iterar sobre estos
            if (step_type == StepType.SELECTONESTEP.value) | (step_type == StepType.SELECTMULTIPLESTEP.value):
                options_to_show_data = step_dictionary.pop('options_to_show')
            step_saved = Step.objects.create(
                workflow=workflow, **step_dictionary)
                # Creo los options to show para cada step, si corresponde
            for idx, options_to_show in enumerate(options_to_show_data, start =1):
                OptionToShow.objects.create(
                    step=step_saved, **options_to_show)
        return workflow

class ProjectSerializer(serializers.ModelSerializer):
	class Meta:
		model = Project
		fields = ('id','name','owner')

class ProjectDetailSerializer(serializers.ModelSerializer):
    workflow = serializers.PrimaryKeyRelatedField(read_only=True)
    created_date = serializers.DateTimeField(format="%Y-%m-%d")
    class Meta:
        model = Project
        fields = ('name','description','workflow','created_date')

class UserSocialAuthSerializer(serializers.ModelSerializer):
    extra_data = serializers.JSONField()
    class Meta:
        model = UserSocialAuth
        fields = ('provider','uid','extra_data')


