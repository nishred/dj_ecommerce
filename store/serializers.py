from rest_framework import serializers

from .models import Product,Collection,Review

from decimal import Decimal 

#A model is the internal representation of a resource stored in the db and a serializer is the external representation of a resource exposed to the external world

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

      