from sre_constants import CATEGORY
from statistics import mode, multimode
from unicodedata import category
from django.db.models.query import QuerySet
from django.db.models.functions import Now
from django.core.validators import MaxValueValidator, MinValueValidator


from django.db.models.signals import post_save
from django.conf import settings
from django.db import models
from django.db.models import Q, F
from django.template.defaultfilters import slugify
from django.shortcuts import reverse
from django_countries.fields import CountryField

CATEGORY_CHOICES = (
    ('S', 'Shirts'),
    ('SW', 'Sport wears'),
    ('OW', 'Outwears'),
    ('D', 'Dresses'),
    ('T', 'T-shirts'),
    ('J', 'Jackets'),
    ('SH', 'Shoes'),
    ('JP', 'Jumpers'),
    ('JN', 'Jeans'),
    ('C', 'Caps'),
)

LABEL_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger'),
)

SHIPPING_CHOICES = (
    ('S', 'standard'),
    ('E', 'express'),
)

ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
)

RATING_CHOICES = (
    ('20%', '1'),
    ('40%', '2'),
    ('60%', '3'),
    ('80%', '4'),
    ('100%', '5'),
)



class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    one_click_purchasing = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    slug = models.SlugField(editable=False)
    description = models.TextField()
    image = models.ImageField()
    image1 = models.ImageField()
    image2 = models.ImageField()
    image3 = models.ImageField()

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        to_slug = f"{self.title}{self.description}"
        self.slug = slugify(to_slug)
        super().save(*args, **kwargs)
 
    def get_absolute_url(self):
        return reverse("estores:product", kwargs={
            'slug': self.slug
        })

    def get_add_to_cart(self):
         return reverse("estores:add-to-cart", kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart(self):
         return reverse("estores:remove-from-cart", kwargs={
            'slug': self.slug
        })
   

    

class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_item_price(self):
        return self.quantity * self.item.price
    
    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    shipping_address = models.ForeignKey(
        'Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey(
        'Address', related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)
    options = models.CharField(max_length=10)

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total
    
    def get_total_coupon(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total

    def get_total_amount_saved(self):
        saved_amount = 0
        total = 0
        for order_item in self.items.all():
            total += order_item.get_amount_saved()
            if self.coupon:
                saved_amount = total + self.coupon.amount
            else:
                saved_amount = total
        return saved_amount
    
    def get_total_add_shipping(self):
        total = self.get_total_coupon()
        if self.options =='Standard':
            total += 750
        elif self.options == 'Express':
            total += 1500
        return total
    
class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    state = models.CharField(max_length=100)
    zip = models.CharField(max_length=100)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Coupon(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=15)
    amount = models.FloatField()
    valid_from = models.DateTimeField(null=True)
    valid_to = models.DateTimeField(null=True)
    max_value = models.IntegerField(validators=[MaxValueValidator(100)], verbose_name='Coupon Quantity', null=True) # No. of coupon
    used = models.IntegerField(default=0)

    class Meta:
        constraints = [
            models.CheckConstraint(check=Q(used__lte=F('max_value')), name="constrain-max-limit")
        ]

    def __str__(self):
        return self.code
    

    
class Budgets(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    budget_name = models.CharField(max_length=12)
    amount = models.FloatField()
    duration = models.CharField(max_length=3)
    date_added = models.DateTimeField(auto_now_add=True)

    
    def __str__(self):
        return self.budget_name
    


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"


def userprofile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        userprofile = UserProfile.objects.create(user=instance)


post_save.connect(userprofile_receiver, sender=settings.AUTH_USER_MODEL)




class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    wished_item = models.ForeignKey(Item, on_delete=models.CASCADE)
    slug = models.CharField(max_length=30, null=True, blank=True)
    added_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.wished_item.title
    

  
class ProductReview(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Item, on_delete=models.CASCADE)
    review_text = models.TextField()
    review_rating = models.CharField(max_length=10, choices=RATING_CHOICES)
    date_added = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def get_review_rating(self):
        return self.review_rating
