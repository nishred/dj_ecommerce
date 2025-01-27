from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from rest_framework.views import APIView

from rest_framework.viewsets import ModelViewSet

from django.db.models import Count

from rest_framework import status

from .models import Product, Collection, Review
from .serializers import ProductSerializer, CollectionSerializer, ReviewSerializer

# Create your views here.

# now the request object becomes the instance of the Request object from the django rest framework

# you must call is_valid() before accessing the validated_data

# A viewset is a class that combines multiple related views(ProductListView and ProductDetailView)
# If you dont wanna perform write operations you can inherit from ReadOnlyModelViewSet


class ProductViewSet(ModelViewSet):

    queryset = Product.objects.all()

    serializer_class = ProductSerializer

    def get_serializer_context(self):
        return {"context": self.request}

    def destroy(self, request, *args, **kwargs):

        instance = self.get_object()

        if instance.orderitems.count() > 0:
            return Response(
                {"success": False, "error": "related order items exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        else:

            self.perform_destroy(instance)

            return Response(
                {"success": True, "message": "Product has been deleted successfully"}
            )

    # overriding the default delete method as we need some custom behaviour
    # def delete(self, request, id):

    #     try:
    #         product = Product.objects.get(id=id)

    #         if product.orderitems.all().count() > 0:
    #             return Response(
    #                 {"success": False, "error": "related order items exist"}
    #             )
    #         else:
    #             product.delete()
    #             return Response({"success": True})
    #     except Exception as e:
    #         return Response({"success": False})


class CollectionViewSet(ModelViewSet):

    queryset = Collection.objects.all()

    serializer_class = CollectionSerializer

    def get_serializer_context(self):
        return {"context": self.request}

    # def delete(self,request,id):

    #     try:

    #         collection = Collection.objects.get(pk = id)

    #         if collection.products.all().count() > 0:
    #             return Response({
    #                 "success" : False,
    #                 "error" : "Related products exist"
    #             })

    #         else:
    #             collection.delete()

    #             return Response({
    #                 "success" : True,
    #                 "message" : "Collection deleted successfully"
    #             })

    #     except Exception as e:
    #         return Response({
    #             "success" : False,
    #             "error" : str(e)
    #         })

    def destroy(self, request, *args, **kwargs):

        instance = self.get_object()

        if instance.products.count() > 0:
            return Response({"success": False, "error": "Related products exist"})

        else:

            self.perform_destroy(instance)

            return Response(
                {"success": True, "message": "Collection has been deleted successfully"}
            )


class ReviewViewSet(ModelViewSet):

    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs["product_pk"])

    def get_serializer_context(self):
        return {"product_id": self.kwargs["product_pk"]}


class ProductList(ListCreateAPIView):

    queryset = Product.objects.select_related("collection").all()

    serializer_class = ProductSerializer

    lookup_field = "id"

    # def get_queryset(self):
    #     return Product.objects.all()

    # def get_serializer_class(self):
    #     return ProductSerializer

    def get_serializer_context(self):
        return {"context": self.request}


class ProductDetail(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = "id"

    # overriding the default delete method as we need some custom behaviour
    def delete(self, request, id):

        try:
            product = Product.objects.get(id=id)

            if product.orderitems.all().count() > 0:
                return Response(
                    {"success": False, "error": "related order items exist"}
                )
            else:
                product.delete()
                return Response({"success": True})
        except Exception as e:
            return Response({"success": False})


# class ProductDetail(APIView):

#     def get(self,request,id):

#         try:
#             product = Product.objects.get(pk = id)

#             serialize = ProductSerializer(product)

#             return Response({
#                 "success" : True,
#                 "product" : serialize.data
#             })
#         except Exception as e:
#             return Response({
#                 "success" : False,
#                 "error" : str(e)
#             })

#     def put(self,request,id):

#           try:

#            product = Product.objects.get(pk = id)

#            deserialized = ProductSerializer(product,data = request.body)


#            if deserialized.is_valid():
#                deserialized.save()

#                return Response({

#                    "success" : True,
#                    "product" : deserialized.data
#                })
#           except Exception as e:
#               return Response({
#                   "success" : True,
#                   "error" : str(e)
#               })


#     def delete(self,request,id):
#       try:
#           product = Product.objects.get(pk = id)

#           if product.orderitems.all.count() > 0:
#               return Response({
#                   "success" : False
#               })
#           else:
#               product.delete()
#               return Response({
#                   "success" : True,
#                   "message" : "product has been deleted successfully"
#               })
#       except Exception as e:
#           return Response({
#               "success" : False,
#               "error" : str(e)
#           })


@api_view(["GET", "POST"])
def get_products(request):

    try:
        if request.method == "GET":
            products = Product.objects.all()

            # when you give the serializer a query set you have to set many = True

            serialized_products = ProductSerializer(products, many=True)

            return Response({"success": True, "data": serialized_products.data})
        elif request.method == "POST":

            serializer = ProductSerializer(data=request.data)

            if serializer.is_valid():
                valdiated_product = serializer.validated_data
                serializer.save()

                print("product", valdiated_product)

                return Response({"success": True})

            else:
                return Response({"success": False, "errors": serializer.errors})

    except Exception as e:
        return Response(
            {"success": False, "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["PUT", "GET", "DELETE"])
def product_detail(request, id):

    product = Product.objects.get(pk=id)

    try:

        if request.method == "GET":

            serializer = ProductSerializer(product)
            return Response(serializer.data)

        elif request.method == "PUT":

            serializer = ProductSerializer(product, data=request.data)

            if serializer.is_valid():

                serializer.save()

                return Response({"success": True, "product": serializer.validated_data})

            else:

                return Response({"success": False, "error": serializer.errors})

        elif request.method == "DELETE":

            if product.orderitems.count() > 0:
                return Response(
                    {
                        "success": False,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            else:

                product.delete()
                return Response(
                    {
                        "success": True,
                        "message": "Product has been deleted successfully",
                    }
                )

    except Exception as e:

        return Response(
            {"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST
        )


# get_objects_or_404 is a shortcut function to get an object or return a 404 error and implements the above logic


@api_view(["GET", "POST"])
def get_collections(request):

    try:
        if request.method == "GET":

            collections = Collection.objects.all().annotate(
                product_count=Count("products")
            )

            serialized = CollectionSerializer(collections, many=True)

            return Response({"success": True, "collections": serialized.data})
        elif request.method == "POST":

            deserialized = CollectionSerializer(data=request.data)

            if deserialized.is_valid():
                deserialized.save()

                return Response(
                    {"success": True, "collection": deserialized.validated_data}
                )

    except Exception as e:

        return Response({"success": True, "error": str(e)})


@api_view(["GET", "PUT", "DELETE"])
def collection_detail(request, id):

    try:

        collection = Collection.objects.get(pk=id).annotate(
            product_count=Count("products")
        )

        if request.method == "GET":

            serialized = CollectionSerializer(collection)

            return Response({"success": True, "collection": serialized.data})

        elif request.method == "PUT":

            deserialized = CollectionSerializer(collection, data=request.data)

            if deserialized.is_valid():

                deserialized.save()

                return Response({"success": True, "collection": deserialized.data})

            else:
                return Response({"success": False})

        elif request.method == "DELETE":

            if collection.products.count() > 0:
                return Response({"success": False})

            else:
                collection.delete()

                return Response(
                    {
                        "success": True,
                        "message": "The collection has been deleted successfully",
                    }
                )

    except Exception as e:
        return Response({"success": False, "error": str(e)})


