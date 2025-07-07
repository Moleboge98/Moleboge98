from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
import uuid

# =================
# CATEGORY MODEL
# =================

class Category(models.Model):
    """Represents a product category."""
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, help_text="A unique, URL-friendly name for the category (e.g., 'fashion-and-apparel').")

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ('name',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """Returns the URL to access a particular category."""
        return reverse('shop:products_by_category', args=[self.slug])

# =================
# USER & AUTH MODELS
# =================

class User(AbstractUser):
    """
    Custom User model that extends Django's AbstractUser.
    Differentiates between 'buyer' and 'vendor' user types.
    Uses email as the unique identifier for login.
    """
    USER_TYPE_CHOICES = (
        ('buyer', 'Buyer'),
        ('vendor', 'Vendor'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='buyer')
    email = models.EmailField(unique=True, help_text="Required. Used for login and notifications.")

    def is_vendor(self):
        return self.user_type == 'vendor'

    def is_buyer(self):
        return self.user_type == 'buyer'
    
    def is_admin(self):
        return self.is_staff

class PasswordResetToken(models.Model):
    """Stores a unique token for a user to reset their password."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_expired(self):
        """Checks if the token has passed its expiration time."""
        return timezone.now() > self.expires_at

# =================
# STORE AND PRODUCT MODELS
# =================

class Store(models.Model):
    """Represents a vendor's storefront."""
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stores', limit_choices_to={'user_type': 'vendor'})
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    """Represents an item for sale in a store."""
    # This is the new category field
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# =================
# ORDER AND CART MODELS
# =================

class Cart(models.Model):
    """Represents a buyer's shopping cart."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart', limit_choices_to={'user_type': 'buyer'})
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart for {self.user.username}"

class CartItem(models.Model):
    """An item within a shopping cart."""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"

class Order(models.Model):
    """Represents a completed order made by a buyer."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='orders', limit_choices_to={'user_type': 'buyer'})
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)


    def __str__(self):
        return f"Order {self.id} by {self.user.username if self.user else 'Deleted User'}"

class OrderItem(models.Model):
    """A specific item within a completed order."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2) # Price at time of purchase

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"

# =================
# REVIEW MODEL
# =================

class Review(models.Model):
    """Represents a review for a product by a user."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField() # You might want to add validators (e.g., MinValueValidator(1), MaxValueValidator(5))
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_verified(self):
        """Checks if the user who wrote the review has actually purchased the product."""
        return Order.objects.filter(user=self.user, items__product=self.product, is_paid=True).exists()

    def __str__(self):
        return f"Review for {self.product.name} by {self.user.username}"
