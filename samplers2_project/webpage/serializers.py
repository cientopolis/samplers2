from rest_framework import serializers
from webpage.models import OptionToShow, Step, Workflow
#import pdb; pdb.set_trace()


class OptionToShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = OptionToShow
        fields = ('text_to_show',)


class StepSerializer (serializers.ModelSerializer):
    def to_representation(self, obj):
        # get the original representation
        ret = super(StepSerializer, self).to_representation(obj)
        if obj.step_type != "TextStep":
        	ret.pop('sample_test')
        	ret.pop('max_length')
        	ret.pop('optional')
        if obj.step_type != "PhotoStep":
        	ret.pop('image_to_overlay')
        	ret.pop('instruct_to_show')
        if (obj.step_type != "SelectOneStep") | (obj.step_type != "SelecMultipleStep"):
        	ret.pop('title')
        	ret.pop('options_to_show')
        if obj.step_type == "PhotoStep":
        	ret.pop('text_to_show')
        return ret
    # remove 'url' field if mobile request
    # if is_mobile_platform(self.context.get('request', None)):
    # ret.pop('url')

    options_to_show = OptionToShowSerializer(many=True, read_only=True)

    class Meta:
        model = Step
        fields = ('step_type', 'text_to_show', 'sample_test', 'max_length', 'optional',
                  'instruct_to_show', 'image_to_overlay', 'title', 'options_to_show')


class WorkflowSerializer(serializers.ModelSerializer):
    steps = StepSerializer(many=True, read_only=True)
    #steps = serializers.StringRelatedField(many=True)

    class Meta:
        model = Workflow
        fields = ('name', 'project', 'steps')
