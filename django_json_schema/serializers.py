from rest_framework import serializers
from .models import JsonValidate
class jsonValidatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = JsonValidate
        fields = ['id', 'url_path', 'json_string', 'json_schema', 'status', 'dt_insert', 'dt_modified']