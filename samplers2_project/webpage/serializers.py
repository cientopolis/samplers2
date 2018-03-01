from rest_framework import serializers
from webpage.models import OptionToShow, Step, Workflow
from webpage.enums import StepType
#import pdb; pdb.set_trace()


class OptionToShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = OptionToShow
        fields = ('text_to_show','order_in_steps')


class StepSerializer (serializers.ModelSerializer):
    def to_representation(self, obj):
        ret = super(StepSerializer, self).to_representation(obj)
        if obj.step_type != StepType.TEXTSTEP.value:
        	ret.pop('sample_test')
        	ret.pop('max_length')
        	ret.pop('optional')
        if obj.step_type != StepType.PHOTOSTEP.value:
        	ret.pop('image_to_overlay')
        	ret.pop('instruct_to_show')
        if (obj.step_type != StepType.SELECTONESTEP.value) & (obj.step_type != StepType.SELECTMULTIPLESTEP.value):
        	ret.pop('title')
        	ret.pop('options_to_show')
        if obj.step_type == StepType.PHOTOSTEP.value:
        	ret.pop('text_to_show')
        return ret
  
    #options_to_show = OptionToShowSerializer(many=True, read_only=True)
    options_to_show = serializers.SerializerMethodField()
    def get_options_to_show(self, instance):
        options_to_show = instance.options_to_show.all().order_by('order_in_steps')
        return OptionToShowSerializer(options_to_show, many=True).data

    class Meta:
        model = Step
        fields = ('step_type', 'text_to_show', 'sample_test', 'max_length', 'optional',
                  'instruct_to_show', 'image_to_overlay', 'title', 'options_to_show')


class WorkflowSerializer(serializers.ModelSerializer):
    #steps = StepSerializer(many=True, read_only=True)
    #steps = serializers.StringRelatedField(many=True)
    steps = serializers.SerializerMethodField()
    class Meta:
        model = Workflow
        fields = ('name', 'project', 'steps')

    def get_steps(self, instance):
        steps = instance.steps.all().order_by('order_in_workflow')
        return StepSerializer(steps, many=True).data
