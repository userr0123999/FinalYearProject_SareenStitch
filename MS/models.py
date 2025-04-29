from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings



from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('admin', 'Admin'),
        ('vendor', 'Vendor'),
    ]

    SIZE_CHOICES = [
        ('XS', 'Extra Small'),
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
        ('Free', 'Free Size'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')
    is_vendor = models.BooleanField(default=False)
    size = models.CharField(max_length=10, choices=SIZE_CHOICES, blank=True, null=True)
    store_name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='vendor_logos/', blank=True, null=True)

    # Avoid conflicts with default User model
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_permissions',
        blank=True
    )

    def __str__(self):
        return self.username


from django.conf import settings

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Saree', 'Saree'),
        ('Lehenga', 'Lehenga'),
        ('Kurtha', 'Kurtha'),
        ('Other', 'Other'),
    ]

    product_name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    category = models.CharField(max_length=255, choices=CATEGORY_CHOICES)

    # 🔥 FIX THIS 🔥
    age_groups = models.ManyToManyField('AgeGroup', blank=True)
    sizes = models.ManyToManyField('Size', blank=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product_name


from django.db import models
from django.conf import settings


class BiddingProduct(models.Model):
    product_name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='bidding/')
    starting_price = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_price = models.DecimalField(max_digits=10, decimal_places=2)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    notified = models.BooleanField(default=False)

    def __str__(self):
        return self.product_name

    def is_active(self):
        now = timezone.now()
        return self.start_time <= now <= self.end_time

    def highest_bid(self):
        return self.bid_set.order_by('-amount').first()

    def bid_count(self):
        return self.bid_set.count()


class Bid(models.Model):
    product = models.ForeignKey(BiddingProduct, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    bid_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username + " - " + str(self.amount)


# models.py

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    payment_method = models.CharField(  # 👉 ADD THIS
        max_length=20,
        choices=[
            ('COD', 'Cash on Delivery'),
            ('eSewa', 'eSewa')
        ],
        default='COD'
    )

    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'), ('shipped', 'Shipped'),
        ('delivered', 'Delivered'), ('cancelled', 'Cancelled')
    ], default='pending')
    order_date = models.DateTimeField(auto_now_add=True)
    delivery_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Order {self.order_id} - {self.product.product_name}"



# Rating Model
from django.conf import settings

class Rating(models.Model):
    rating_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    thrift = models.ForeignKey('ThriftProduct', on_delete=models.CASCADE, null=True, blank=True)
    rating = models.PositiveSmallIntegerField()
    review = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        target = self.product.product_name if self.product else self.thrift.product.product_name
        return f"Rating {self.rating} for {target}"



class Chat(models.Model):
    thrift = models.ForeignKey('ThriftProduct', on_delete=models.CASCADE, related_name='chats')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,null=True)
    vendor = models.ForeignKey('MS.Vendor', on_delete=models.CASCADE, null=True)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages',
                                  null=True)

    def __str__(self):
        vendor_name = self.vendor.store_name if self.vendor else "No Vendor"
        return f"{self.sender.username} -> {vendor_name}: {self.message}"


# Coupon Model
class Coupon(models.Model):
    coupon_id = models.AutoField(primary_key=True)
    user = models.CharField(max_length=50)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    coupon_code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    expiry_date = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"Coupon {self.coupon_code}"


# models.py

class CartItem(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=10, default="M")
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.product_name}"



# WishlistItem Model
class WishlistItem(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.product_name}"


# ContactMessage Model
class ContactMessage(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    contact = models.CharField(max_length=20)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.email}"


# ThriftProduct Model
CONDITION_CHOICES = [
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5 - Excellent'),
]
class ThriftProduct(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, null=True)
    condition_rating = models.CharField(max_length=1, choices=CONDITION_CHOICES)
    approval_status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='pending')
    is_sold = models.BooleanField(default=False)  # ✅ New Field
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.product.product_name} - {self.condition_rating}/5"


# Vendor Model
from django.conf import settings

class Vendor(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # ✅ already correct if you did this
    store_name = models.CharField(max_length=255)
    store_description = models.TextField()
    logo = models.ImageField(upload_to='vendors/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.store_name

from django.db import models
from django.conf import settings
from django.utils import timezone

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=timezone.now)
    type = models.CharField(max_length=50, default='general')  # e.g., 'chat', 'order', 'thrift'

    def __str__(self):
        return f"{self.user.username} - {self.message[:30]}"


class ThriftComment(models.Model):
    thrift = models.ForeignKey(ThriftProduct, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


from django.db import models
from django.conf import settings  # 👈 This ensures we use the custom user model

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to='profile_pics/', default='profile_pics/default.png')

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Size(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class AgeGroup(models.Model):
    label = models.CharField(max_length=100)

    def __str__(self):
        return self.label
