import json
import re
from jsonschema import Draft7Validator
from django.http import JsonResponse
from django.utils import timezone
from .models import JsonValidate
from .serializers import jsonValidatorSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['POST'])
def insert_json(request):
    if request.method == 'POST':
        data = request.data
        url_path = data.get('url_path')
        json_string = data.get('json_string')
        json_schema = data.get('json_schema')

        existing_instance = JsonValidate.objects.filter(url_path=url_path).first()

        if existing_instance:
            existing_instance.json_string = json_string
            existing_instance.json_schema = preprocess_json_schema(json_schema)
            existing_instance.dt_modified = timezone.now()
            existing_instance.save()  # Simpan perubahan

            serializer = jsonValidatorSerializer(instance=existing_instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            json_schema_convert = preprocess_json_schema(json_schema)
            json_data = {
                'url_path': url_path,
                'json_string': json_string,
                'json_schema': json_schema_convert,
                'status': 1,
            }

            serializer = jsonValidatorSerializer(data=json_data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({'detail': 'Metode HTTP tidak didukung'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


def preprocess_json_schema(json_schema):
    json_schema_convert = re.sub(r'"type":\s*"str"', r'type: "string"', json_schema)
    json_schema_convert = re.sub(r'"type":\s*"dict"', r'type: "object"', json_schema_convert)
    json_schema_convert = re.sub(r'(".*?":\s*)(".*?")', r'\1\2', json_schema_convert)
    json_schema_convert = re.sub(r'"required":\s*\[([^\]]*)\]', r'required: [\1]', json_schema_convert)
    return json_schema_convert

@api_view(['POST'])
def generate_json_schema(request):
    if request.method == 'POST':
        data = request.data.get('json_string', {})

        try:
            json_data = json.loads(data)
        except json.JSONDecodeError:
            return Response({'detail': 'Data yang diberikan bukan JSON'}, status=status.HTTP_400_BAD_REQUEST)

        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {},
            "required": []
        }

        for key, value in json_data.items():
            schema["properties"][key] = {"type": type(value).__name__}
            schema["required"].append(key)

        validator = Draft7Validator(schema)
        schema = validator.schema

        return Response(schema, status=status.HTTP_200_OK)

    return Response({'detail': 'Metode HTTP tidak didukung'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)