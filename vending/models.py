from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver


def validate_price(value):
    if value % 5 != 0:
        raise ValidationError(
            _('%(value)s is not in expected range'),
            params={'value': value},
        )


def validate_seller_id(value):
    seller = VendingUser.objects.filter(role='seller', id=value).first()
    if not bool(seller):
        raise ValidationError(
            _('This seller_id doesn\'t exist.'),
            params={'value': value},
        )


class Product(models.Model):
    name = models.CharField(max_length=120, unique=True)
    cost = models.IntegerField(validators=[validate_price])
    amount_available = models.IntegerField()
    seller_id = models.IntegerField(validators=[validate_seller_id])

    def __str__(self) -> str:
        return self.name


class VendingUser(AbstractUser):
    is_login = models.BooleanField(default=False)
    CHOICES = (
        ('seller', 'Seller'),
        ('buyer', 'Buyer'),
    )
    role = models.CharField(max_length=6, choices=CHOICES)
    deposit = models.IntegerField(validators=[validate_price])

    def save(self, *args, **kwargs):
        if self.role == "seller":
            # this condtion for sellers, sets to zero
            self.deposit = 0
        if self.is_superuser:
            # this condition for createsuperuser via cli
            self.deposit = 0
            self.role = 'seller'

        return super(VendingUser, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return self.username
