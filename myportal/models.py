import uuid
from django.db import models


class Resource(models.Model):
    uuid = models.CharField(default=uuid.uuid4, editable=False, unique=True, max_length=50)
    resource_type = models.CharField(default="single", max_length=50)
    path = models.CharField(max_length=255)
    task_id = models.CharField(max_length=50)

    def __str__(self):
        return f"Resource {self.uuid}: resource_type = {self.resource_type}, filepath = {self.path}, task_id = {self.task_id}"
