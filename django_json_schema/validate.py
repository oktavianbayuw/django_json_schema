import json
from django.http import JsonResponse
from .models import JsonValidate
from django.utils import timezone
from jsonschema import validate, exceptions
import jsonschema
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
        json_schema = data.get('json_schema')

        try:
            json_data = JsonValidate.objects.get(url_path=url_path)
        except JsonValidate.DoesNotExist:
            return Response({'detail': 'Skema JSON tidak ditemukan'}, status=status.HTTP_404_NOT_FOUND)

        json_string = data.get('json_string')

        # Validasi apakah json_schema adalah objek JSON yang valid
        try:
            json_schema_dict = json.loads(json_schema)
        except json.JSONDecodeError:
            return Response({'detail': 'Skema JSON tidak valid'}, status=status.HTTP_400_BAD_REQUEST)

        # Periksa apakah json_string adalah JSON yang valid sesuai dengan schema
        try:
            validate(instance=json.loads(json_string), schema=json_schema_dict)
            # JSON valid
            status_value = 1
            errors = None
        except exceptions.ValidationError as e:
            # JSON tidak valid
            status_value = 0
            errors = [str(error) for error in e.errors]

        json_data.status = status_value
        json_data.dt_modified = timezone.now()
        json_data.save()

        if status_value == 1:
            return Response({'detail': 'Data JSON valid'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Data JSON tidak valid', 'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'detail': 'Metode HTTP tidak didukung'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)