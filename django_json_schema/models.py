from django.db import models

class JsonValidate(models.Model):
    url_path = models.CharField(max_length=200)
    json_string = models.JSONField()
    json_schema = models.TextField()
    dt_insert = models.DateTimeField(auto_now_add=True)
    dt_modified = models.DateTimeField(auto_now_add=True)
    status = models.SmallIntegerField()