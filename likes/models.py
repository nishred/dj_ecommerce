from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Like(models.Model):

    user = models.ForeignKey(User,on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType,on_delete=models.CASCADE)    # for identifying the type of object that a user likes
    object_id = models.PositiveIntegerField()  # for refering to the actual object
    content_object = GenericForeignKey("content_type","object_id")  # for reading the object

    

