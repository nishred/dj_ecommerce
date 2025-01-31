from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from ..models import Customer


# This receiver logic runs after every save(creations and updates as well)

@receiver(post_save,sender = settings.AUTH_USER_MODEL)
def create_customer_for_user(sender,**kwargs):
    if kwargs["created"]:
        user = kwargs["instance"]
        customer = Customer.objects.create(user_id = user.id)



