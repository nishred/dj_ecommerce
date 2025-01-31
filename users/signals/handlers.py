from store.signals import order_created

from django.dispatch import receiver

from store.serializers import CreateOrderSerializer


@receiver(order_created,sender = CreateOrderSerializer)
def on_order_creation(sender,**kwargs):
    print(kwargs.get("order"))

