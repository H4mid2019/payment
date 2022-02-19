from django.contrib import admin
from .models import VendingUser, Product

@admin.register(VendingUser)
class VendingUser(admin.ModelAdmin):
    list_display = ('username', 'role', 'deposit')

@admin.register(Product)
class Product(admin.ModelAdmin):
    pass
