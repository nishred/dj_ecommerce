from django.shortcuts import render

from django.http import HttpResponse, JsonResponse

from django.core.exceptions  import ObjectDoesNotExist

from django.db.models import Q,F
from store.models import Product, OrderItem, Order, Customer, Collection, Promotion, Address, Cart,CartItem,Review


# Create your views here.


def say_hello(request):
    return JsonResponse({

      "success" : True,
      "data" : "vedere manvitha Reddys"

    })



def get_ordered_products(request):

    # Order -> OrderItem -> Product

     try:

      
       orders = Order.objects.prefetch_related("items__product").select_related("customer").all().order_by("-placed_at")[:5]


       order_list = list(orders)

       return JsonResponse({
           
         "success" : True,
         "orders" : order_list


       })


                 

     except Exception as e:
         return JsonResponse({
             
           "success" : False,
           "error" : str(e)

         })

   

    


 
     
    

