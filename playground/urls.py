from . import views

from django.urls import path

urlpatterns = [
path("sayhello/",views.say_hello),
path("products/",views.get_ordered_products)
]