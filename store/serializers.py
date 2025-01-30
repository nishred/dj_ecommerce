from rest_framework import serializers

from .models import Product,Collection,Review, Cart, CartItem, Customer, OrderItem, Order

from django.db import transaction

from django.conf import settings

from decimal import Decimal

from django.contrib.auth import get_user_model


User = get_user_model()

# A model is the internal representation of a resource stored in the db and a serializer is the external representation of a resource exposed to the external world

# DB model(model) vs API model(serializer)

# note: the name of the fields dont have to match


class CollectionSerializer(serializers.ModelSerializer):
      
      class Meta:
            model  = Collection
            fields = ["id","title","product_count"]


      product_count = serializers.IntegerField(read_only = True)

      # product_count = serializers.SerializerMethodField(method_name="get_product_count",read_only = True)


      # def get_product_count(self,collection: Collection):

      #       return collection.products.all().count()      


# class ProductSerializer(serializers.Serializer):

#         id = serializers.IntegerField()
#         title = serializers.CharField(max_length = 255)
#         price = serializers.DecimalField(max_digits=6,decimal_places=2,source = "unit_price")
#         price_with_tax = serializers.SerializerMethodField(method_name="calculate_tax")
#         collection = CollectionSerializer()

#         def calculate_tax(self,product: Product):
#             return product.unit_price * Decimal(1.1)

# the serializer is a class that is used to convert complex data types like query sets and model instances to native python data types that can be dueasily rendered into json,xml or other content types

# read-only fields are only used for output(serialization)
# The write-only fields are only used for input(deserialization)
# read-write fields are used for both output and input
# method fields are only used for output
# method_field = serializers.SerializerMethodField(method_name = "pendu")

# In Django REST Framework (DRF), all fields that are explicitly defined in the serializer class (whether they are read-only, write-only, or read-write) must be included in the fields list in the Meta class.

class ProductSerializer(serializers.ModelSerializer):
      class Meta:
            model = Product
            fields = ["id","title","unit_price","price_with_tax","collection","inventory","slug","description","collection_id"]

      price_with_tax = serializers.SerializerMethodField(method_name="calculate_tax")

      collection  = CollectionSerializer(read_only = True)

      collection_id = serializers.PrimaryKeyRelatedField(

        write_only  = True,
        queryset = Collection.objects.all(),
        source = "collection"

      )

      def calculate_tax(self,product:Product):
            return product.unit_price*Decimal(1.1)
      

      # override the create method of the ModelSerializer class
      # def create(self, validated_data):
      #       product = Product(**validated_data)
      #       product.other = 2
      #       product.save()


      #responsible for updating an existing instance given the validated data


#       def update(self, instance, validated_data):
#     """
#     Update and return an existing Product instance, given the validated data.
#     """
#     # Add an additional field (e.g., updated_by) to validated_data
#     validated_data["updated_by"] = self.context["request"].user

#     # Update the instance with the validated data
#     instance.title = validated_data.get("title", instance.title)
#     instance.unit_price = validated_data.get("unit_price", instance.unit_price)
#     instance.updated_by = validated_data.get("updated_by", instance.updated_by)

#     # Save the updated instance
#     instance.save()

#     return instance


class ReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = ["id","name","description","product_id","date","product"]

    # enforcing the referential intergrity constraints at the api level
    product_id = serializers.PrimaryKeyRelatedField(

                  write_only = True,
                  queryset = Product.objects.all(),
                  source = "product"
            )

    product = ProductSerializer(read_only = True)

    def create(self, validated_data):
        review = Review.objects.create(product_id = self.context["product_id"],**validated_data)
        return review


class CartItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = CartItem
        fields = ["id", "product_id", "product", "quantity", "total_price"]

    id = serializers.UUIDField(read_only=True)

    total_price = serializers.SerializerMethodField(
        read_only=True, method_name="get_total_price"
    )

    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source="product",
        write_only=True,
        required=False,
    )

    product = ProductSerializer(read_only=True)

    # self.instance is the model instance

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance:
            self.fields["product_id"].required = True

    def get_total_price(self, cartitem: CartItem):
        return cartitem.quantity * cartitem.product.unit_price


class CartSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cart
        fields = ["id", "created_at", "total_price", "items"]

    id = serializers.UUIDField(read_only=True)

    total_price = serializers.SerializerMethodField(
        method_name="get_total_price", read_only=True
    )
    
    created_at = serializers.DateTimeField(read_only = True)

    items = CartItemSerializer(many=True, read_only=True)

    def get_total_price(self, cart: Cart):

        total_price = 0

        items = cart.items.all()

        for item in items:
            item_price = item.quantity * item.product.unit_price
            total_price += item_price
        return total_price


class CustomerSerializer(serializers.ModelSerializer):
     
    class Meta:
         model  = Customer
         fields = ["id","birth_date","membership","phone"]


    id = serializers.IntegerField(read_only = True)    



class OrderItemSerializer(serializers.ModelSerializer):
     class Meta:
          model = OrderItem
          fields = ["id","product_id","quantity","unit_price","product"]

     product_id = serializers.PrimaryKeyRelatedField(
           queryset = Product.objects.all(),
           source = "product",
           write_only = True
     )     

     product = ProductSerializer(read_only = True)

     id = serializers.IntegerField(read_only = True)



class OrderSerializer(serializers.ModelSerializer):
     
     class Meta:
          model = Order
          fields = ["id","payment_status","items","placed_at","customer"]

     placed_at = serializers.DateTimeField(read_only = True)   

     items = OrderItemSerializer(many = True, read_only = True) 

     id = serializers.IntegerField(read_only = True)

     customer = CustomerSerializer(read_only = True)
 

     def save(self, **kwargs):
          
          print("save arguments",kwargs)  
          return super().save(**kwargs)    

     def create(self, validated_data):
          print("validated data",validated_data)

          return super().create(validated_data)

class UpdateOrderSerializer(serializers.ModelSerializer):

     class Meta:
          model = Order
          fields = ["payment_status"]     


class CreateOrderSerializer(serializers.Serializer):
   
      cart_id = serializers.UUIDField()

      def validate_cart_id(self,value):
           if not Cart.objects.filter(pk = value).exists():
                raise serializers.ValidationError("Cart doesnt exist")
           else:
                return value


      def create(self, validated_data):

                print("Validated data",validated_data)
                
                cart_id = validated_data.get("cart_id")  
                customer_id = validated_data.get("customer_id")

                print("customer details",customer_id)

                cart = Cart.objects.get(pk = cart_id)

                with transaction.atomic():
                     
                     order = Order.objects.create(customer_id = customer_id)

                     cartitems = cart.items.all()

                     for item in cartitems:     
                          order.items.create(order_id = order.id,product_id = item.product_id,quantity = item.quantity,unit_price = item.product.unit_price)

                     cart.delete()

                     return order     
                
