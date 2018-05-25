from rest_framework import serializers
from webpage.models import OptionToShow, Step, Workflow, Project
from webpage.enums import StepType
import pdb


class OptionToShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = OptionToShow
        fields = ('text_to_show','next_step_id')
        
    def to_representation(self, obj):
        ret = super(OptionToShowSerializer, self).to_representation(obj)
        pdb.set_trace()         
        if (obj.step.step_type != StepType.SELECTONESTEP.value):
            ret.pop('next_step_id')
        return ret


class StepSerializer (serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(StepSerializer, self).to_representation(obj)          
        if obj.step_type != StepType.TEXTSTEP.value:
            ret.pop('sample_test')
            ret.pop('max_length')
            ret.pop('optional')
        if obj.step_type != StepType.PHOTOSTEP.value:
            ret.pop('photo_instructions')
        if (obj.step_type != StepType.SELECTONESTEP.value) & (obj.step_type != StepType.SELECTMULTIPLESTEP.value):
            ret.pop('title')
            ret.pop('options_to_show')  
        if obj.step_type == StepType.PHOTOSTEP.value:
            ret.pop('text_to_show')
        if obj.step_type == StepType.ROUTESTEP.value:
            ret.pop('interval')
            ret.pop('map_zoom')
        if obj.step_type == StepType.SOUNDRECORDSTEP.value:
            ret.pop('instructions_to_show')
        return ret
    options_to_show = serializers.SerializerMethodField()

    def get_options_to_show(self, instance):
        options_to_show = instance.options_to_show.all().order_by('order_in_steps')
        return OptionToShowSerializer(options_to_show, many=True).data

    class Meta:
        model = Step
        fields = ('step_type', 'next_step_id', 'text_to_show', 'sample_test', 'max_length', 'optional',
                  'photo_instructions', 'title', 'options_to_show')


class StepSerializerPost (serializers.ModelSerializer):
    options_to_show = OptionToShowSerializer(many=True, required=False)

    class Meta:
        model = Step
        fields = ('step_type', 'next_step_id','text_to_show', 'sample_test', 'max_length', 'input_type', 'optional',
                  'title', 'options_to_show','photo_instructions','interval','map_zoom','instructions_to_show')
        #read_only_fields = ('next_step_id',)


class WorkflowSerializer(serializers.ModelSerializer):
    steps = serializers.SerializerMethodField()

    class Meta:
        model = Workflow
        fields = ('name', 'project', 'steps')

    def get_steps(self, instance):
        steps = instance.steps.all().order_by('order_in_workflow')
        return StepSerializer(steps, many=True).data


class WorkflowSerializerPost(serializers.ModelSerializer):
    steps = StepSerializerPost(many=True)

    class Meta:
        model = Workflow
        fields = ('name', 'project', 'steps')

    def create(self, validated_data):
        steps_data = validated_data.pop('steps')
        workflow = Workflow.objects.create(**validated_data)
        order_in_workflow = 1
        index = 0
        for step in steps_data:
            step["order_in_workflow"] = order_in_workflow
            step_dictionary = steps_data[index]
            step_type = step_dictionary['step_type']
            # Si es de estos tipos, saco los options_to_show para desp iterar sobre estos, ya que sino tira error
            if (step_type == StepType.SELECTONESTEP.value) | (step_type == StepType.SELECTMULTIPLESTEP.value):
                options_to_show_data = step_dictionary.pop('options_to_show')
            step_saved = Step.objects.create(
                workflow=workflow, **step_dictionary)
            order_in_workflow = order_in_workflow + 1
            order_in_steps = 1
            index = index + 1
            if (step_type == StepType.SELECTONESTEP.value) | (step_type == StepType.SELECTMULTIPLESTEP.value):
                # Creo los options to show para cada step, si corresponde
                for options_to_show in options_to_show_data:
                    options_to_show["order_in_steps"] = order_in_steps
                    OptionToShow.objects.create(
                        step=step_saved, **options_to_show)
                    order_in_steps = order_in_steps + 1
        return workflow

    def update(self, instance, validated_data):
        workflow = Workflow.objects.get(id= instance.id)
        workflow.delete()
        steps_data = validated_data.pop('steps')
        workflow = Workflow.objects.create(id=instance.id,**validated_data)
        order_in_workflow = 1
        index = 0
        for step in steps_data:
            step["order_in_workflow"] = order_in_workflow
            step_dictionary = steps_data[index]
            step_type = step_dictionary['step_type']
            # Si es de estos tipos, saco los options_to_show para desp iterar sobre estos, ya que sino tira error
            if (step_type == StepType.SELECTONESTEP.value) | (step_type == StepType.SELECTMULTIPLESTEP.value):
                options_to_show_data = step_dictionary.pop('options_to_show')
            step_saved = Step.objects.create(
                workflow=workflow, **step_dictionary)
            order_in_workflow = order_in_workflow + 1
            order_in_steps = 1
            index = index + 1
            if (step_type == StepType.SELECTONESTEP.value) | (step_type == StepType.SELECTMULTIPLESTEP.value):
                # Creo los options to show para cada step, si corresponde
                for options_to_show in options_to_show_data:
                    options_to_show["order_in_steps"] = order_in_steps
                    OptionToShow.objects.create(
                        step=step_saved, **options_to_show)
                    order_in_steps = order_in_steps + 1
        return instance

class ProjectSerializer(serializers.ModelSerializer):
	workflow = serializers.PrimaryKeyRelatedField(read_only=True)
	class Meta:
		model = Project
		fields = ('id','name','workflow')

