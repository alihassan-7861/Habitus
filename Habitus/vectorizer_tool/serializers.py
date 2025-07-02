from rest_framework import serializers

class VectorizerSerializer(serializers.Serializer):
    image = serializers.ImageField(required=True)
    # width = serializers.FloatField(min_value=0.0, max_value=1.0E12, required=False)
    # height = serializers.FloatField(min_value=0.0, max_value=1.0E12, required=False)
    mode = serializers.ChoiceField(
        choices=[
            ("test", "test"),
            ("preview", "preview"),
            ("production", "production"),
        ],
        default="test"
    )
    output_format = serializers.ChoiceField(choices=[("svg", "svg"), ("png", "png")], default='svg', required=False)
    level_of_details = serializers.FloatField(min_value=0.01, max_value=10.0, default=0.1, required=False)
    smoothing = serializers.ChoiceField(choices=[("aliased", "aliased"), ("anti_aliased", "anti_aliased")],default='anti_aliased',required=False)
    minimum_area = serializers.FloatField(min_value=45.0, max_value=100.0, default=0.125, required=False)
    maximum_colors = serializers.IntegerField(min_value=0, max_value=256, default=0, required=False)
