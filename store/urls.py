from django.urls import path
from . import views

from rest_framework_nested import routers

router = routers.DefaultRouter()

router.register("products",views.ProductViewSet)
router.register("collections",views.CollectionViewSet)

# so we will have look up field as product_pk in the url

# parent router, parent prefix and a lookup

product_router = routers.NestedDefaultRouter(router,"products",lookup = "product")

product_router.register("reviews",views.ReviewViewSet,basename="product-reviews")

urlpatterns = router.urls + product_router.urls

# if you use pk here, looup_field not needed

# urlpatterns = [
#    path("products/",views.ProductList.as_view()),
#    # path("products/<id>",views.product_detail)
#    path("products/<int:id>",views.ProductDetail.as_view()),
#    path("collections/",views.get_collections),
#    path("collections/<int:id>",views.collection_detail)
# 


