from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from vending.models import VendingUser, Product
from rest_framework.authtoken.models import Token
import string
import random


def random_string(x=random.randrange(5, 15, 1)):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(x))


class ProductTest(TestCase):
    sample_password = "foo+secretpass"
    api_client = APIClient()
    seller_token_key = ""
    buyer_token_key = ""
    buyer_username = ""
    sample_product_name = ''
    sample_product_cost = ''
    seller_id = ''
    buyer_deposit = 0

    def setUp(self):
        sample_cost = [random.randrange(5, 550, 5) for _ in range(1000)]
        user_seller_id = []
        # creating sample sellers (user with seller role) for creating sample products
        for _ in range(0, 10):
            user = VendingUser(email=f"{random_string()}@{random_string()}.com", username=random_string(),
                               role="seller")
            user.set_password(self.sample_password)
            user.save()
            user_seller_id.append(user.id)

        # creating sample products
        for _ in range(6, 15):
            Product.objects.create(name=random_string(), amount_available=random.randrange(0, 15, 1),
                                   cost=random.choices(sample_cost)[0], seller_id=random.choice(user_seller_id))

        sample_product = Product.objects.create(name=random_string(), amount_available=10, cost=50,
                                                seller_id=user.id)
        self.sample_product_name = sample_product.name
        self.sample_product_cost = sample_product.cost
        self.seller_id = user.id
        token = Token.objects.create(user=user)
        self.seller_token_key = token.key
        buyer_username, buyer_email, buyer_deposit = random_string(), f"{random_string()}@{random_string()}.com", random.randrange(
            100, 850, 5)
        buyer_user = VendingUser(email=buyer_email, username=buyer_username, deposit=buyer_deposit, role="buyer")
        buyer_user.set_password(self.sample_password)
        buyer_user.save()
        self.buyer_username = buyer_username
        self.buyer_deposit = buyer_deposit
        buyer_token = Token.objects.create(user=buyer_user)
        self.buyer_token_key = buyer_token.key

    def test_setup_approval(self):
        """ This method approve the setup worked perfectly, which means the model and setup logic are working"""
        users_count = VendingUser.objects.count()
        self.assertEqual(11, users_count)
        buyer_count = VendingUser.objects.filter(role="buyer").count()
        self.assertEqual(1, buyer_count)
        token_counts = Token.objects.count()
        self.assertEqual(token_counts, 2)
        product_counts = Product.objects.count()
        self.assertEqual(product_counts, 10)

    def test_credential_check(self):
        """ test for conditionals, to be sure without token doesn't work"""
        response = self.api_client.post('/api/products',
                                        {"name": "test", "cost": 20, "amount_available": 10, "seller_id": 2},
                                        format="json")
        self.assertEqual(response.status_code, 401)
        self.assertTrue(response.data.get("detail"))

    def test_deposit(self):
        random_deposit = random.choice([5, 10, 20, 50, 100])
        # adding deposit by the buyer user account via the api client
        self.api_client.credentials(HTTP_AUTHORIZATION='Token ' + self.buyer_token_key)
        response = self.api_client.patch(reverse("deposit"), {"deposit": random_deposit}, format="json")
        self.assertEqual(response.status_code, 201)
        buyer = VendingUser.objects.filter(role="buyer", username=self.buyer_username).first()
        self.assertEqual(buyer.deposit, self.buyer_deposit + random_deposit)

    def test_deposit_wrong_coins(self):
        random_deposit = random.choice([i for i in range(5, 500) if i not in [5, 10, 20, 50, 100]])
        # adding deposit by the buyer user account via the api client
        self.api_client.credentials(HTTP_AUTHORIZATION='Token ' + self.buyer_token_key)
        response = self.api_client.patch(reverse("deposit"), {"deposit": random_deposit}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.get('coin_type'), 'only use acceptable coins.')
        # buyer credit didn't change
        buyer = VendingUser.objects.filter(role="buyer", username=self.buyer_username).first()
        self.assertEqual(buyer.deposit, self.buyer_deposit)

    def test_deposit_empty_deposit_field(self):
        self.api_client.credentials(HTTP_AUTHORIZATION='Token ' + self.buyer_token_key)
        response = self.api_client.patch(reverse("deposit"), format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.get('coin_type'), 'only use acceptable coins.')
        # buyer credit didn't change
        buyer = VendingUser.objects.filter(role="buyer", username=self.buyer_username).first()
        self.assertEqual(buyer.deposit, self.buyer_deposit)

    def test_buy(self):
        self.api_client.credentials(HTTP_AUTHORIZATION='Token ' + self.buyer_token_key)
        response = self.api_client.post(reverse("buy"), {"name": self.sample_product_name}, format="json")
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.data.get("product_name"), self.sample_product_name)
        self.assertEqual(response.data.get("spent"), self.sample_product_cost)

    def test_buy_product_doesnt_exist(self):
        product_names = list(Product.objects.values_list('name', flat=True))
        random_name = random_string(12)
        random_product_name = random_name if random_name not in product_names else random_string(15)
        self.api_client.credentials(HTTP_AUTHORIZATION='Token ' + self.buyer_token_key)
        response = self.api_client.post(reverse("buy"), {"name": random_product_name}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.get("product"), "the requested product isn't available.")

    def test_buy_empty_product_input(self):
        self.api_client.credentials(HTTP_AUTHORIZATION='Token ' + self.buyer_token_key)
        response = self.api_client.post(reverse("buy"), format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.get("product"), "You have to enter product name to your request body.")

    def test_buy_product_zero_amount_available(self):
        Product.objects.create(name='test_foo', amount_available=0, cost=50, seller_id=self.seller_id)
        self.api_client.credentials(HTTP_AUTHORIZATION='Token ' + self.buyer_token_key)
        response = self.api_client.post(reverse("buy"), {"name": 'test_foo'}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.get("product"), "the requested product isn't available.")

    def test_buy_buyer_deposit_zero(self):
        """ Buying a product while the buyer doesn't have any deposit"""
        self.api_client.credentials(HTTP_AUTHORIZATION='Token ' + self.buyer_token_key)
        # make sure the buyer deposit would be zero
        reset_response = self.api_client.post(reverse("reset"), format="json")
        self.assertEqual(reset_response.status_code, 201)
        response = self.api_client.post(reverse("buy"), {"name": self.sample_product_name}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.get("deposit"), "insufficient balance, please deposit more coins.")

    def test_delete_product(self):
        self.api_client.credentials(HTTP_AUTHORIZATION='Token ' + self.seller_token_key)
        response = self.api_client.delete(f"/api/product/{self.sample_product_name}")
        self.assertEqual(response.status_code, 204)
        # check the product doesn't exist in db
        product = Product.objects.filter(name=self.sample_product_name).first()
        self.assertFalse(bool(product))

    def test_delete_product_does_not_exist(self):
        product_names = list(Product.objects.values_list('name', flat=True))
        random_name = random_string(12)
        random_product_name = random_name if random_name not in product_names else random_string(15)
        self.api_client.credentials(HTTP_AUTHORIZATION='Token ' + self.seller_token_key)
        response = self.api_client.delete(f"/api/product/{random_product_name}")
        self.assertEqual(response.status_code, 400)
        self.assertEqual("This product doesn't exist", response.data.get("name"))

    def test_delete_from_another_seller_account(self):
        user = VendingUser(email=f"{random_string()}@{random_string()}.com", username=random_string(),
                           role="seller")
        user.set_password(self.sample_password)
        user.save()
        token = Token.objects.create(user=user)
        self.api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.api_client.delete(f"/api/product/{self.sample_product_name}")
        self.assertEqual(response.status_code, 400)
        self.assertEqual("you can\'t delete this product.", response.data.get("seller_id"))
