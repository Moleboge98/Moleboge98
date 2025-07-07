from django.contrib import admin
from .models import Category, Product, Store, Order, OrderItem, Review, User

# This customizes how the Category model appears in the admin.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    # This line automatically creates the URL-friendly 'slug' from the 'name'.
    prepopulated_fields = {'slug': ('name',)}

# This customizes how the Product model appears in the admin.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'store', 'price', 'stock', 'category', 'created_at']
    list_filter = ['category', 'store']
    list_editable = ['price', 'stock']

# This registers the rest of your models with the admin site using the default options.
admin.site.register(Store)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Review)

# Note: The custom User model is usually registered automatically, but if it's not
# showing up, you can add it here. Django's default UserAdmin is very powerful.
# from django.contrib.auth.admin import UserAdmin
# admin.site.register(User, UserAdmin)
