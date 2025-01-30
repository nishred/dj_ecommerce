from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .pagination import CustomPageNumberPagination
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import (
    CreateModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
    UpdateModelMixin,
    ListModelMixin
)

from rest_framework.permissions import IsAuthenticated

from rest_framework.viewsets import ModelViewSet, GenericViewSet

from django.db.models import Count

from rest_framework import status

from .models import Product, Collection, Review, Cart, CartItem, Customer, OrderItem, Order
from .serializers import (
    ProductSerializer,
    CollectionSerializer,
    ReviewSerializer,
    CartSerializer,
    CartItemSerializer,
    CustomerSerializer,
    OrderItemSerializer,
    OrderSerializer,
    UpdateOrderSerializer,
    CreateOrderSerializer
)

# Create your views here.

# now the request object becomes the instance of the Request object from the django rest framework

# you must call is_valid() before accessing the validated_data

# A viewset is a class that combines multiple related views(ProductListView and ProductDetailView)
# If you dont wanna perform write operations you can inherit from ReadOnlyModelViewSet


class ProductViewSet(ModelViewSet):

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["collection_id"]
    # you can even add related fields here
    search_fields = ["title", "description", "collection__title"]

    ordering_fields = ["unit_price", "last_update"]
    pagination_class = CustomPageNumberPagination

    # def get_queryset(self):

    #     queryset = Product.objects.all()

    #     collection_id = self.request.query_params.get("collection_id")

    #     if collection_id is not None:
    #         queryset = queryset.filter(collection_id=collection_id)

    #     return queryset

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

# when we are creating a new order, all we need to send to the server is just the cart_id

class CartViewSet(
    CreateModelMixin, GenericViewSet, RetrieveModelMixin, DestroyModelMixin
):

    # for each item you want to prefetch the product as well
    queryset = Cart.objects.prefetch_related("items__product").all()

    serializer_class = CartSerializer



class CartItemViewSet(ModelViewSet):

    serializer_class = CartItemSerializer


    def get_queryset(self):
        cart_id = self.kwargs.get("cart_pk")

        return CartItem.objects.select_related("product").filter(cart_id=cart_id)

    def perform_create(self, serializer):
        cart_id = self.kwargs.get("cart_pk")

        serializer.save(cart_id=cart_id)

    def update(self, request, *args, **kwargs):

        cartitem = self.get_object()

        serializer = self.get_serializer(cartitem, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "data": serializer.validated_data})
        else:
            return Response({"success": False, "errors": serializer.errors})


class CustomerViewSet(CreateModelMixin,UpdateModelMixin,RetrieveModelMixin,GenericViewSet):

      serializer_class = CustomerSerializer
      queryset = Customer.objects.all()

      permission_classes = [IsAuthenticated]

      # if detail is set to false, the action is available on the list view /customers/me

      # if detail is set to true, the action will be available on the detail view /customers/pk/true
   
      # The request.user will be populated with the User model instance by the auth middleware


      def perform_create(self, serializer):
          serializer.save(user_id = self.request.user.id)

      @action(detail=False,methods=["PUT","GET"])
      def me(self,request):
         
         try:
              
            customer = Customer.objects.get(user_id = request.user.id)

            print("customer",customer)

            if request.method == "GET":
                serializer = self.get_serializer(customer)

                return Response({
                   "success" : True,
                   "customer" : serializer.data

                })

            elif request.method == "PUT":
                serializer = self.get_serializer(customer,data = request.data)

                if serializer.is_valid():
                    serializer.save()
                    return Response({
                        "success" : True,
                        "customer" : serializer.validated_data
                    })
                else:
                    return Response({
                      "success" : False,
                      "errors" : serializer.errors
                 
                    })
         except Exception as e:  
             return Response({
                 "success" : False,
                 "error" : str(e)
             })
    

class OrderItemViewSet(ModelViewSet):

    serializer_class = OrderItemSerializer

    def get_queryset(self):
        order_id = self.kwargs.get("order_pk")

        return OrderItem.objects.filter(order_id = order_id)
    
    def update(self, request, *args, **kwargs):

        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance,data = request.data,partial = True)

            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success" : True,
                    "data" : serializer.validated_data
                })    
            else:
                return Response({
                    "success" : False,
                    "errors" : serializer.errors
                })
        except Exception as e:
            return Response({
                "success" : False,
                "error" : str(e)
            })    

class OrderViewSet(ListModelMixin,CreateModelMixin,RetrieveModelMixin,DestroyModelMixin,GenericViewSet):


    permission_classes = [IsAuthenticated]


    def create(self, request, *args, **kwargs):
       serializer = self.get_serializer(data = request.data)
       
       if serializer.is_valid():
           self.perform_create(serializer = serializer)
           response_serializer = OrderSerializer(serializer.instance)

           return Response({
               "success" : True,
               "order" : response_serializer.data
             })


    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return UpdateOrderSerializer
        elif self.request.method == "GET":
            return OrderSerializer
        elif self.request.method == "POST":
            return CreateOrderSerializer

    def get_queryset(self):

        customer = Customer.objects.get(user_id = self.request.user.id)
        return Order.objects.filter(customer_id = customer.id)


    def perform_create(self, serializer):

        customer = Customer.objects.get(user_id = self.request.user.id)
        print("customer",customer.id)
        serializer.save(customer_id = customer.id)


# class CartItemViewSet(ModelViewSet):
#     http_method_names = ["get", "post", "patch", "delete"]

#     def get_serializer_class(self):
#         if self.request.method == "POST":
#             return AddCartItemSerializer
#         elif self.request.method == "PATCH":
#             return UpdateCartItemSerializer
#         return CartItemSerializer

#     def get_serializer_context(self):
#         return {"cart_id": self.kwargs["cart_pk"]}

#     def get_queryset(self):
#         return CartItem.objects.filter(cart_id=self.kwargs["cart_pk"]).select_related(
#             "product"
#         )


# class AddCartItemSerializer(serializers.ModelSerializer):
#     product_id = serializers.IntegerField()

#     def validate_product_id(self, value):
#         if not Product.objects.filter(pk=value).exists():
#             raise serializers.ValidationError("No product with the given ID was found.")
#         return value

#     def save(self, **kwargs):
#         cart_id = self.context["cart_id"]
#         product_id = self.validated_data["product_id"]
#         quantity = self.validated_data["quantity"]

#         try:
#             cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
#             cart_item.quantity += quantity
#             cart_item.save()
#             self.instance = cart_item
#         except CartItem.DoesNotExist:
#             self.instance = CartItem.objects.create(
#                 cart_id=cart_id, **self.validated_data
#             )

#         return self.instance

#     class Meta:
#         model = CartItem
#         fields = ["id", "product_id", "quantity"]


# class UpdateCartItemSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CartItem
#         fields = ["quantity"]


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





