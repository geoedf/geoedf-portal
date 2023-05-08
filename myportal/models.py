import uuid
from django.db import models


class Resource(models.Model):
    uuid = models.CharField(default=uuid.uuid4, editable=False, unique=True, max_length=50)
    resource_type = models.CharField(default="single", max_length=50)
    publication_name = models.CharField(max_length=255)
    path = models.CharField(max_length=255)
    task_id = models.CharField(null=True, max_length=50)
    user_id = models.CharField(null=True, max_length=50)
    created_time = models.DateTimeField(null=True, auto_now_add=True)
    modified_time = models.DateTimeField(null=True, auto_now=True)

    def __str__(self):
        return f"Resource {self.uuid}: " \
               f"resource_type = {self.resource_type}, filepath = {self.path}, task_id = {self.task_id}, " \
               f"created_time = {self.created_time}"
