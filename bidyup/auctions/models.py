from django.db import models
from django.contrib.auth.models import AbstractUser

# กรณีอยากใช้ User เองแทน Django default
class User(AbstractUser):
    ROLE_CHOICES = (
        ('Seller', 'Seller'),
        ('Bidder', 'Bidder'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Item(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('closed', 'Closed'),
    )
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    image = models.CharField(max_length=255, blank=True, null=True)  # หรือ ImageField
    starting_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    end_time = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="items")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="items")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Bid(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    time = models.DateTimeField(auto_now_add=True)
    is_winner = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="bids")
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")

class Order(models.Model):
    PAYMENT_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
    )
    DELIVERY_CHOICES = (
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    )
    item = models.OneToOneField(Item, on_delete=models.CASCADE, related_name="order")
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    payment_status = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='pending')
    delivery_status = models.CharField(max_length=10, choices=DELIVERY_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Favourite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favourites")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="favourited_by")

    class Meta:
        unique_together = ('user', 'item')
