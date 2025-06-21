from rest_framework import serializers

class VectorizerSerializer(serializers.Serializer):
    image = serializers.ImageField()
    width = serializers.CharField(required=False)
    height = serializers.CharField(required=False)
    mode = serializers.ChoiceField(
        choices=[
            ("test", "test"),
            ("preview", "preview"),
            ("production", "production"),
        ],
        default="test"
    )
    output_format = serializers.ChoiceField(choices=[("svg", "svg"), ("png", "png")])
    level_of_details = serializers.CharField(required=False)
    smoothing = serializers.ChoiceField(choices=[("aliased", "aliased"), ("un-aliased", "un-aliased")])
    minimum_area = serializers.CharField(required=False)
    maximum_colors = serializers.CharField(required=False)
