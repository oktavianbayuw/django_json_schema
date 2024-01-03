import json
from jsonschema import Draft7Validator
from django.http import JsonResponse
from .models import JsonValidate
from .serializers import jsonValidatorSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['GET'])
def list_all_data(request):
    if request.method =='GET':
        all_data_json = JsonValidate.objects.all()
        serializer = jsonValidatorSerializer(all_data_json, many=True)
        return JsonResponse({"data" : serializer.data})

@api_view(['GET'])
def get_data_by_url_path(request):
    if request.method == 'GET':
        url_path = request.query_params.get('url_path', None)
        if url_path is None:
            return Response({'detail': 'Parameter url_path tidak diberikan'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            json_data = JsonValidate.objects.get(url_path=url_path)
        except JsonValidate.DoesNotExist:
            return Response({'detail': 'Data tidak ditemukan'}, status=status.HTTP_404_NOT_FOUND)
        serializer = jsonValidatorSerializer(json_data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response({'detail': 'Metode HTTP tidak didukung'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['DELETE'])
def delete_data_by_url_path(request, url_path):
    if request.method == 'DELETE':
        try:
            json_data = JsonValidate.objects.get(url_path=url_path)
        except JsonValidate.DoesNotExist:
            return Response({'detail': 'Data tidak ditemukan'}, status=status.HTTP_404_NOT_FOUND)

        json_data.delete()

        return Response({'detail': 'Data berhasil dihapus'}, status=status.HTTP_204_NO_CONTENT)

    return Response({'detail': 'Metode HTTP tidak didukung'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST'])
def validate_json(request):
    if request.method == 'POST':
        data = request.data
        url_path = data.get('url_path')

        try:
            json_data = JsonValidate.objects.get(url_path=url_path)
            json_schema = json.loads(json_data.json_schema)
        except JsonValidate.DoesNotExist:
            return Response({'detail': 'Skema JSON tidak ditemukan'}, status=status.HTTP_404_NOT_FOUND)
        except json.JSONDecodeError:
            return Response({'detail': 'Skema JSON tidak valid'}, status=status.HTTP_400_BAD_REQUEST)

        print("JSON Schema:", json_schema)
        json_string = data.get('json_string')

        validator = Draft7Validator(json_schema)
        errors = list(validator.iter_errors(json.loads(json_string)))

        if not errors:
            json_data.status = 1
            return Response({'detail': 'Data JSON valid'}, status=status.HTTP_200_OK)
        else:
            json_data.status = 0
            return Response({'detail': 'Data JSON tidak valid', 'errors': [error.message for error in errors]}, status=status.HTTP_400_BAD_REQUEST)

        # Simpan perubahan status ke database
        json_data.save()

        return Response({'detail': 'Validasi berhasil, status diubah'}, status=status.HTTP_200_OK)

    return Response({'detail': 'Metode HTTP tidak didukung'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)