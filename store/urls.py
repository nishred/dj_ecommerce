from django.urls import path
from . import views


urlpatterns = [
   path("products/",views.get_products),
   # path("products/<id>",views.product_detail)
   path("products/<int:id>",views.product_detail)
]