from rest_framework import serializers

from .models import Product

from decimal import Decimal 



#A model is the internal representation of a resource stored in the db and a serializer is the external representation of a resource exposed to the external world

# note: the name of the fields dont have to match

class ProductSerializer(serializers.Serializer):

        id = serializers.IntegerField()
        title = serializers.CharField(max_length = 255)
        unit_price = serializers.DecimalField(max_digits=6,decimal_places=2)
        price_with_tax = serializers.SerializerMethodField(method_name="calculate_tax")

        def calculate_tax(self,product: Product):
            return product.unit_price * Decimal(1.1)           

# the serializer is a class that is used to convert complex data types like query sets and model instances to native python data types that can be easily rendered into json,xml or other content types