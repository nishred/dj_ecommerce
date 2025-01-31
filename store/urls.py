from django.urls import path,include
from . import views

from rest_framework_nested import routers
router = routers.DefaultRouter()

router.register("products",views.ProductViewSet)

router.register("collections",views.CollectionViewSet)

router.register("customers",views.CustomerViewSet)

router.register("orders",views.OrderViewSet,basename="order")

router.register("carts",views.CartViewSet,basename="carts")


order_router = routers.NestedDefaultRouter(router,"orders",lookup = "order")

cart_items_router = routers.NestedDefaultRouter(router,"carts",lookup = "cart")


# so we will have look up field as product_pk in the url

# parent router, parent prefix and a lookup

cart_items_router.register("items",views.CartItemViewSet,basename  = "cart-items")

order_router.register("items",views.OrderItemViewSet,basename="order-items")

product_router = routers.NestedDefaultRouter(router,"products",lookup = "product")

product_router.register("reviews",views.ReviewViewSet,basename="product-reviews")

# urlpatterns = router.urls + product_router.urls + order_router.urls + cart_items_router.urls

# if you use pk here, looup_field not needed

# urlpatterns = [
#    path("products/",views.ProductList.as_view()),
#    # path("products/<id>",views.product_detail)
#    path("products/<int:id>",views.ProductDetail.as_view()),
#    path("collections/",views.get_collections),
#    path("collections/<int:id>",views.collection_detail)


urlpatterns = [
  path("",include(router.urls)),
  path("",include(product_router.urls)),
  path("",include(cart_items_router.urls)),
  path("",include(order_router.urls))
]

