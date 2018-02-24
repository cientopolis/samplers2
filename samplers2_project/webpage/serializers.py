from rest_framework import serializers

class OptionToShowSerializer(serializers.ModelSerializer):
	class Meta:
		model = OptionToShow
		fields = ('text_to_show')

class StepSerializer (serializers.ModelSerializer):
	options_to_show = OptionToShowSerializer
	class Meta:
		model = StepSerializer
		fields('step_type','text_to_show','sample_text','max_length','optional','image_to_show','image_to_overlay','title','options_to_show')


