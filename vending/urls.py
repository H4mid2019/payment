from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import ProductViewSet, create_auth, BuyerProductViewSet, UserViewSet


urlpatterns = [
    path('products', ProductViewSet.as_view({
        'get': 'list',
        'post': 'create'
    })),
    path('product/<int:product_id>', ProductViewSet.as_view({
        'put': 'update',
        'delete': 'destroy',
        'get': 'retrieve_one'
    })),
    path('user/<str:username>', UserViewSet.as_view({
        'patch': 'update',
        'delete': 'destroy',
        'get': 'read'
    })),
    path('get_token', obtain_auth_token, name='get_auth_token'),
    path("create_user", create_auth, name="create_user"),

    path("buyer/deposit", BuyerProductViewSet.as_view({'patch': 'deposit'}), name="deposit"),
    path("buyer/reset", BuyerProductViewSet.as_view({'post': 'reset'}), name="reset"),
    path("buyer/buy", BuyerProductViewSet.as_view({'post': 'buy'}), name="buy")
]