import uuid
from django.db import models


class Resource(models.Model):
    uuid = models.CharField(default=uuid.uuid4, editable=False, unique=True, max_length=50)
    resource_type = models.CharField(default="single", max_length=50)
    publication_name = models.CharField(max_length=255)
    description = models.CharField(max_length=1024, null=True)
    path = models.CharField(max_length=255)
    task_id = models.CharField(null=True, max_length=50)
    status = models.CharField(null=True, max_length=50)
    user_id = models.CharField(null=True, max_length=50)
    created_time = models.DateTimeField(null=True, auto_now_add=True)
    modified_time = models.DateTimeField(null=True, auto_now=True)
    extra_info = models.CharField(max_length=1024, null=True)

    def __str__(self):
        return f"Resource {self.uuid}: " \
               f"resource_type = {self.resource_type}, filepath = {self.path}, task_id = {self.task_id}, " \
               f"user_id = {self.user_id}, created_time = {self.created_time}"


class FileInfo(models.Model):
    path = models.URLField()
    info = models.CharField(max_length=255)

    def __str__(self):
        return self.path