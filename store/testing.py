from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Like(models.Model):
    
   name = models.CharField(max_length=255)
   content_type = models.ForeignKey(ContentType,on_delete=models.CASCADE)
   object_id = models.PositiveIntegerField()
   content_object = GenericForeignKey()

