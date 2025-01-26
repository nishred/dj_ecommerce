from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework import status

from .models import Product
from .serializers import ProductSerializer

# Create your views here.

# now the request object becomes the instance of the Request object from the django rest framework
@api_view() 
def get_products(request):

     try:
          products  = Product.objects.all()

          # when you give the serializer a query set you have to set many = True  
 
          serialized_products = ProductSerializer(products,many = True)

          return Response({
            "success" : True, 
            "data" : serialized_products.data

          })
     except Exception as e:
         return Response({
            "success" : False,
            "error" : str(e)
         },status = status.HTTP_500_INTERNAL_SERVER_ERROR)  



@api_view()
def product_detail(request,id):
    
    try:
      
      product = Product.objects.get(pk = id)

      serializer = ProductSerializer(product)

      return Response(serializer.data)
    
    except Product.DoesNotExist:
      
      return Response({
         
        "success" : False,
        "error" : "Product not found"
           
      },status = status.HTTP_404_NOT_FOUND)
  
# get_objects_or_404 is a shortcut function to get an object or return a 404 error and implements the above logic
