from django.contrib import admin
from .models import VendingUser, Product


@admin.register(VendingUser)
class VendingUser(admin.ModelAdmin):
    list_display = ('username', 'role', 'deposit')
    list_filter = ('role', )


@admin.register(Product)
class Product(admin.ModelAdmin):
    list_display = ("name", "amount_available", "cost", "seller_id")
    list_filter = ("cost", "seller_id")
