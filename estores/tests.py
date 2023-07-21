from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from datetime import datetime
from pytz import timezone
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Item, OrderItem, Order, UserProfile, Address, Payment, Coupon, Budgets

class ItemModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create an item for testing
        cls.item = Item.objects.create(
            title="Test Item",
            price=100.0,
            category="A",
            label="X",
            description="Test description",
            image=SimpleUploadedFile("test_image.jpg", b"dummy content"),
            image1=SimpleUploadedFile("test_image1.jpg", b"dummy content"),
            image2=SimpleUploadedFile("test_image2.jpg", b"dummy content"),
            image3=SimpleUploadedFile("test_image3.jpg", b"dummy content"),
        )

    def test_str_method(self):
        # Test the __str__ method
        self.assertEqual(str(self.item), "Test Item")

    def test_slug_creation(self):
        # Test the save method and slug creation
        expected_slug = "test-itemtest-description"
        self.assertEqual(self.item.slug, expected_slug)

    def test_absolute_url(self):
        # Test the get_absolute_url method
        expected_url = reverse("estores:product", kwargs={'slug': self.item.slug})
        self.assertEqual(self.item.get_absolute_url(), expected_url)

    def test_add_to_cart_url(self):
        # Test the get_add_to_cart method
        expected_url = reverse("estores:add-to-cart", kwargs={'slug': self.item.slug})
        self.assertEqual(self.item.get_add_to_cart(), expected_url)

    def test_remove_from_cart_url(self):
        # Test the get_remove_from_cart method
        expected_url = reverse("estores:remove-from-cart", kwargs={'slug': self.item.slug})

# Test for orderitem model

class OrderItemModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a test user
        cls.User = get_user_model()
        cls.user = cls.User.objects.create_user(username="testuser", password="testpassword")

        # Create a test item
        cls.item = Item.objects.create(
            title="Test Item",
            price=100.0,
            description="Test description",
            image="test_image.jpg",
        )

    def test_str_method(self):
        # Test the __str__ method
        order_item = OrderItem.objects.create(user=self.user, item=self.item, quantity=3)
        self.assertEqual(str(order_item), "3 of Test Item")

    def test_get_total_item_price(self):
        # Test the get_total_item_price method
        order_item = OrderItem.objects.create(user=self.user, item=self.item, quantity=2)
        expected_total_item_price = 2 * 100.0  # price is 100.0
        self.assertEqual(order_item.get_total_item_price(), expected_total_item_price)

    def test_get_total_discount_item_price(self):
        # Test the get_total_discount_item_price method with a discount price
        order_item = OrderItem.objects.create(user=self.user, item=self.item, quantity=3)
        order_item.item.discount_price = 80.0  # discounted price is 80.0
        expected_total_discount_item_price = 3 * 80.0
        self.assertEqual(order_item.get_total_discount_item_price(), expected_total_discount_item_price)

    def test_get_amount_saved(self):
        # Test the get_amount_saved method with a discount price
        order_item = OrderItem.objects.create(user=self.user, item=self.item, quantity=4)
        order_item.item.discount_price = 70.0  # discounted price is 70.0
        expected_amount_saved = 4 * (100.0 - 70.0)
        self.assertEqual(order_item.get_amount_saved(), expected_amount_saved)

    def test_get_final_price_with_discount(self):
        # Test the get_final_price method with a discount price
        order_item = OrderItem.objects.create(user=self.user, item=self.item, quantity=5)
        order_item.item.discount_price = 90.0  # discounted price is 90.0
        self.assertEqual(order_item.get_final_price(), 5 * 90.0)

    def test_get_final_price_without_discount(self):
        # Test the get_final_price method without a discount price
        order_item = OrderItem.objects.create(user=self.user, item=self.item, quantity=1)
        self.assertEqual(order_item.get_final_price(), 100.0)

#Test case for Address

User = get_user_model()

class AddressModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpassword"
        )

    def test_address_creation(self):
        # Create an Address instance
        address = Address.objects.create(
            user=self.user,
            street_address="Test Street",
            apartment_address="Test Apartment",
            country="US",
            state="Test State",
            zip="12345",
            address_type="S",
            default=True,
        )

        # Retrieve the created address from the database
        retrieved_address = Address.objects.get(pk=address.pk)

        # Check if the retrieved address matches the created address
        self.assertEqual(retrieved_address.user, self.user)
        self.assertEqual(retrieved_address.street_address, "Test Street")
        self.assertEqual(retrieved_address.apartment_address, "Test Apartment")
        self.assertEqual(retrieved_address.country, "US")
        self.assertEqual(retrieved_address.state, "Test State")
        self.assertEqual(retrieved_address.zip, "12345")
        self.assertEqual(retrieved_address.address_type, "S")
        self.assertTrue(retrieved_address.default)

    def test_address_str_method(self):
        address = Address.objects.create(
            user=self.user,
            street_address="Test Street",
            apartment_address="Test Apartment",
            country="US",
            state="Test State",
            zip="12345",
            address_type="S",
            default=True,
        )
        self.assertEqual(str(address), "testuser")

#test for coupon 
User = get_user_model()

class CouponModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpassword"
        )

    def test_coupon_creation(self):
        tz = timezone('UTC')
        valid_from = datetime(2023, 7, 1, 0, 0, tzinfo=tz)
        valid_to = datetime(2023, 8, 1, 0, 0, tzinfo=tz)

        # Create a Coupon instance
        coupon = Coupon.objects.create(
            user=self.user,
            code="TESTCOUPON",
            amount=10.00,
            valid_from=valid_from,
            valid_to=valid_to,
            max_value=100,
            used=0,
        )

        # Retrieve the created coupon from the database
        retrieved_coupon = Coupon.objects.get(pk=coupon.pk)

        # Check if the retrieved coupon matches the created coupon
        self.assertEqual(retrieved_coupon.user, self.user)
        self.assertEqual(retrieved_coupon.code, "TESTCOUPON")
        self.assertEqual(retrieved_coupon.amount, 10.00)
        self.assertEqual(retrieved_coupon.valid_from, valid_from)
        self.assertEqual(retrieved_coupon.valid_to, valid_to)
        self.assertEqual(retrieved_coupon.max_value, 100)
        self.assertEqual(retrieved_coupon.used, 0)

    def test_coupon_str_method(self):
        tz = timezone('UTC')
        valid_from = datetime(2023, 7, 1, 0, 0, tzinfo=tz)
        valid_to = datetime(2023, 8, 1, 0, 0, tzinfo=tz)

        coupon = Coupon.objects.create(
            user=self.user,
            code="TESTCOUPON",
            amount=10.00,
            valid_from=valid_from,
            valid_to=valid_to,
            max_value=100,
            used=0,
        )
        self.assertEqual(str(coupon), "TESTCOUPON")

#test for budget


User = get_user_model()

class BudgetsModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpassword"
        )

    def test_budgets_creation(self):
        # Create a Budgets instance
        budgets = Budgets.objects.create(
            user=self.user,
            budget_name="Test Budget",
            amount=1000.00,
            duration="30",
        )

        # Retrieve the created budgets from the database
        retrieved_budgets = Budgets.objects.get(pk=budgets.pk)

        # Check if the retrieved budgets match the created budgets
        self.assertEqual(retrieved_budgets.user, self.user)
        self.assertEqual(retrieved_budgets.budget_name, "Test Budget")
        self.assertEqual(retrieved_budgets.amount, 1000.00)
        self.assertEqual(retrieved_budgets.duration, "30")

    def test_budgets_str_method(self):
        budgets = Budgets.objects.create(
            user=self.user,
            budget_name="Test Budget",
            amount=1000.00,
            duration="30",
        )
        self.assertEqual(str(budgets), "Test Budget")

