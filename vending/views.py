from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from django.db import transaction
from .models import Product, VendingUser
from .serializers import ProductSerializer, UserSerializer
import logging

logger = logging.getLogger(__name__)


class safe_methods(BasePermission):
    def has_permission(self, request, view):
        return request.method == 'GET'


class OnlySellers(BasePermission):
    def has_permission(self, request, view):
        if request.method != 'GET':
            return VendingUser.objects.filter(username=request.user, role="seller").exists()


class ProductViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated & OnlySellers | safe_methods]

    def list(self, request):
        """this method retruns the all products
        """
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer._errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, name=None):
        user_id = VendingUser.objects.filter(username=request.user).first().id
        with transaction.atomic():
            product = Product.objects.select_for_update().get(name=name)
            if not bool(product):
                return Response({"name": "This product doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
            if product.seller_id != user_id:
                return Response({"seller_id": "you can\'t update this product."}, status=status.HTTP_400_BAD_REQUEST)
            request_seller_id = request.data.get("seller_id")
            if request_seller_id and request_seller_id != product.seller_id:
                return Response({"seller_id": "seller_id it's not changeable."}, status=status.HTTP_400_BAD_REQUEST)
            serialezer = ProductSerializer(product, data=request.data)
            if serialezer.is_valid(raise_exception=True):
                serialezer.save()
                return Response(serialezer.data, status=status.HTTP_202_ACCEPTED)

    def destroy(self, request, name=None):
        user_id = VendingUser.objects.filter(username=request.user).first().id
        with transaction.atomic():
            try:
                product = Product.objects.select_for_update().get(name=name)
            except Product.DoesNotExist:
                return Response({"name": "This product doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
            if product.seller_id != user_id:
                return Response({"seller_id": "you can\'t delete this product."}, status=status.HTTP_400_BAD_REQUEST)
            product.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


def remain_coins(j):
    arr = []
    while j >= 5:
        if j >= 100:
            j -= 100
            arr.append(100)
        elif j >= 50:
            j -= 50
            arr.append(50)
        elif j >= 20:
            arr.append(20)
            j -= 20
        elif j >= 10:
            arr.append(10)
            j -= 10
        elif j >= 5:
            arr.append(j)
            j -= 5
    return arr


class OnlyBuyers(BasePermission):
    def has_permission(self, request, view):
        return VendingUser.objects.filter(username=request.user, role="buyer").exists()


class BuyerProductViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated & OnlyBuyers | safe_methods]

    def deposit(self, request):
        """this view function deposit into buyer account, accepts only PATCH requests, for users with buyer roles.
        """
        acceptable_coins = [5, 10, 20, 50, 100]
        with transaction.atomic():
            request_deposit = request.data.get("deposit")
            if request_deposit not in acceptable_coins:
                return Response({"coin_type": "only use acceptable coins."}, status=status.HTTP_400_BAD_REQUEST)
            target_user = VendingUser.objects.select_for_update().get(username=request.user)
            serialized = UserSerializer(target_user, data={"deposit": request_deposit + target_user.deposit},
                                        partial=True)
            if serialized.is_valid(raise_exception=True):
                serialized.save()
                return Response(serialized.data, status=status.HTTP_201_CREATED)
            return Response(serialized._errors, status=status.HTTP_400_BAD_REQUEST)

    def reset(self, request):
        with transaction.atomic():
            target_user = VendingUser.objects.select_for_update().get(username=request.user)
            serialized = UserSerializer(target_user, data={"deposit": 0}, partial=True)
            if serialized.is_valid(raise_exception=True):
                serialized.save()
                return Response(serialized.data, status=status.HTTP_201_CREATED)
            return Response(serialized._errors, status=status.HTTP_400_BAD_REQUEST)

    def buy(self, request):
        with transaction.atomic():
            request_product_name = request.data.get("name", False)
            if not request_product_name:
                return Response({"product": "You have to enter product name to your request body."},
                                status=status.HTTP_400_BAD_REQUEST)
            try:
                product = Product.objects.select_for_update().get(name=request_product_name)
            except Product.DoesNotExist:
                return Response({"product": "the requested product isn't available."},
                                status=status.HTTP_400_BAD_REQUEST)
            if product.amount_available < 1:
                logger.error(f"this product amount available is zero : {product.name}")
                return Response({"product": "the requested product isn't available."},
                                status=status.HTTP_400_BAD_REQUEST)
            target_user = VendingUser.objects.select_for_update().get(username=request.user)
            if target_user.deposit < product.cost:
                logger.warning(f'This user doesn\'t have sufficient balance: {target_user.username}')
                return Response({"deposit": "insufficient balance, please deposit more coins."},
                                status=status.HTTP_400_BAD_REQUEST)
            final_deposit = target_user.deposit - product.cost
            coins = remain_coins(final_deposit)
            serialized = UserSerializer(target_user, data={"deposit": final_deposit}, partial=True)
            product_serialezed = ProductSerializer(product, data={"amount_available": product.amount_available - 1},
                                                   partial=True)
            if serialized.is_valid(raise_exception=True):
                serialized.save()
            else:
                return Response(serialized._errors, status=status.HTTP_400_BAD_REQUEST)
            if product_serialezed.is_valid(raise_exception=True):
                product_serialezed.save()
                return Response(
                    {"spent": product.cost, "product_id": product.id, "product_name": product.name, "change": coins},
                    status=status.HTTP_202_ACCEPTED)
            return Response(product_serialezed._errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((AllowAny,))
def create_auth(request):
    """this view function creates a user so then the user can obtain a token
    """
    role = request.data.get("role", False)
    deposit = request.data.get("deposit", False)
    if role == 'seller' and bool(deposit):
        logger.warning(f'someone tried to make a user with seller role with deposit username: {request.data.get("username")}')
        return Response({"deposit": "seller doesn\'t need to deposit. :-("}, status=status.HTTP_400_BAD_REQUEST)
    serialized = UserSerializer(data=request.data)
    if serialized.is_valid(raise_exception=True):
        serialized.save()
        return Response(serialized.data, status=status.HTTP_201_CREATED)
    return Response(serialized._errors, status=status.HTTP_400_BAD_REQUEST)
