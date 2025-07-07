from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

app_name = 'shop'

urlpatterns = [
    # =================
    # GENERAL & HOME
    # =================
    path('', views.home, name='home'),
    path('notes/', views.notes_view, name='notes'),
    path('category/<slug:category_slug>/', views.home, name='products_by_category'),

    # =================
    # USER & AUTHENTICATION
    # All user-related URLs are grouped here.
    # =================
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # path('profile/', views.profile_view, name='profile'),

    # Password Reset URLs
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='shop/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='shop/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='shop/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='shop/password_reset_complete.html'), name='password_reset_complete'),

    # =================
    # PRODUCTS & VENDOR
    # URLs for viewing products and for vendor-specific actions.
    # =================
    path('products/<int:product_id>/', views.product_detail_view, name='product_detail'),
    path('products/<int:product_id>/add_review/', views.add_review_view, name='add_review'),
    path('vendor/dashboard/', views.vendor_dashboard_view, name='vendor_dashboard'),
    path('vendor/store/create/', views.create_store_view, name='create_store'),
    path('vendor/product/add/', views.add_product_view, name='add_product'),
    path('vendor/product/<int:product_id>/edit/', views.edit_product_view, name='edit_product'),
    path('vendor/product/<int:product_id>/delete/', views.delete_product_view, name='delete_product'),

    # =================
    # CART, CHECKOUT & ORDERS
    # URLs for the entire shopping and checkout process.
    # =================
    path('cart/', views.view_cart_view, name='view_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart_view, name='add_to_cart'),
    path('cart/item/<int:cart_item_id>/remove/', views.remove_from_cart_view, name='remove_from_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('order/<int:order_id>/confirmation/', views.order_confirmation_view, name='order_confirmation'),

    # =================
    # ADMIN
    # The include for your custom admin dashboard.
    # This assumes 'shop/admin_urls.py' exists.
    # =================
    path('admin/dashboard/', include('shop.admin_urls')),
]
