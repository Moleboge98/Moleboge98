from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.http import require_POST

# ADDED Category to the import list
from .models import Product, Store, Review, Cart, CartItem, Order, OrderItem, Category 
from .forms import (
    UserRegistrationForm,
    UserLoginForm,
    StoreForm,
    ProductForm,
    ReviewForm
)

# =================
# HELPER FUNCTIONS
# =================

def is_buyer_check(user):
    """Checks if a user is authenticated and is a buyer."""
    return user.is_authenticated and user.is_buyer()

def is_vendor_check(user):
    """Checks if a user is authenticated and is a vendor."""
    return user.is_authenticated and user.is_vendor()

# =================
# GENERAL & HOME VIEWS
# =================

# UPDATED the home view to handle category filtering
def home(request, category_slug=None):
    """
    Displays the homepage.
    Can be optionally filtered by a category slug.
    """
    categories = Category.objects.all()
    products = Product.objects.all().order_by('-created_at')
    current_category = None

    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=current_category)

    context = {
        'products': products,
        'categories': categories,
        'current_category': current_category
    }
    return render(request, 'shop/home.html', context)


def notes_view(request):
    """Displays a simple notes page."""
    return render(request, 'shop/notes.html')

def product_detail_view(request, product_id):
    """Displays the details for a single product, including reviews."""
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all().order_by('-created_at')
    review_form = ReviewForm()
    return render(request, 'shop/product_detail.html', {'product': product, 'reviews': reviews, 'review_form': review_form})

# =================
# AUTHENTICATION VIEWS
# =================

def register_view(request):
    """Handles user registration for both buyers and vendors."""
    if request.user.is_authenticated:
        return redirect('shop:home')
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            if user.is_vendor():
                return redirect('shop:create_store')
            return redirect('shop:home')
    else:
        form = UserRegistrationForm()
    return render(request, 'shop/register.html', {'form': form})

def login_view(request):
    """Handles user login."""
    if request.user.is_authenticated:
        return redirect('shop:home')
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('shop:home')
            else:
                # Add an error message for invalid login
                pass
    else:
        form = UserLoginForm()
    return render(request, 'shop/login.html', {'form': form})

@login_required
def logout_view(request):
    """Logs the current user out."""
    logout(request)
    return redirect('shop:home')

# =================
# VENDOR & STORE VIEWS
# =================

@login_required
@user_passes_test(is_vendor_check, login_url='shop:home')
def vendor_dashboard_view(request):
    """Displays the dashboard for a vendor, showing their store and products."""
    store = get_object_or_404(Store, owner=request.user)
    products = Product.objects.filter(store=store)
    return render(request, 'shop/vendor_dashboard.html', {'store': store, 'products': products})

@login_required
@user_passes_test(is_vendor_check, login_url='shop:home')
def create_store_view(request):
    """Handles the creation of a new store by a vendor."""
    if Store.objects.filter(owner=request.user).exists():
        return redirect('shop:vendor_dashboard')
    if request.method == 'POST':
        form = StoreForm(request.POST)
        if form.is_valid():
            store = form.save(commit=False)
            store.owner = request.user
            store.save()
            return redirect('shop:vendor_dashboard')
    else:
        form = StoreForm()
    return render(request, 'shop/create_store.html', {'form': form})

@login_required
@user_passes_test(is_vendor_check, login_url='shop:home')
def add_product_view(request):
    """Handles the creation of a new product by a vendor."""
    store = get_object_or_404(Store, owner=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.store = store
            product.save()
            return redirect('shop:vendor_dashboard')
    else:
        form = ProductForm()
    return render(request, 'shop/add_product.html', {'form': form})

@login_required
@user_passes_test(is_vendor_check, login_url='shop:home')
def edit_product_view(request, product_id):
    """Handles editing an existing product by a vendor."""
    product = get_object_or_404(Product, id=product_id, store__owner=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('shop:vendor_dashboard')
    else:
        form = ProductForm(instance=product)
    return render(request, 'shop/edit_product.html', {'form': form, 'product': product})

@require_POST 
@login_required
@user_passes_test(is_vendor_check, login_url='shop:home')
def delete_product_view(request, product_id):
    """Handles deleting an existing product by a vendor."""
    product = get_object_or_404(Product, id=product_id, store__owner=request.user)
    product.delete()
    return redirect('shop:vendor_dashboard')


# =================
# CART, CHECKOUT & ORDER VIEWS
# =================

@login_required
@user_passes_test(is_buyer_check, login_url='shop:home')
def view_cart_view(request):
    """Displays the contents of the buyer's shopping cart."""
    cart, _ = Cart.objects.get_or_create(user=request.user)
    return render(request, 'shop/cart.html', {'cart': cart})

@login_required
@user_passes_test(is_buyer_check, login_url='shop:home')
def add_to_cart_view(request, product_id):
    """Adds a product to the buyer's cart or increments its quantity."""
    product = get_object_or_404(Product, id=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
    cart_item.save()
    return redirect('shop:view_cart')

@require_POST
@login_required
@user_passes_test(is_buyer_check, login_url='shop:home')
def remove_from_cart_view(request, cart_item_id):
    """Removes an item from the buyer's cart."""
    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user=request.user)
    cart_item.delete()
    return redirect('shop:view_cart')

@login_required
@user_passes_test(is_buyer_check, login_url='shop:home')
def checkout_view(request):
    """Handles the checkout process, creating an order from the cart."""
    cart = get_object_or_404(Cart, user=request.user)
    if not cart.items.exists():
        return redirect('shop:home')

    total_price = sum(item.product.price * item.quantity for item in cart.items.all())
    order = Order.objects.create(user=request.user, total_price=total_price)

    for item in cart.items.all():
        OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity, price=item.product.price)
        # Decrease stock
        product = item.product
        product.stock -= item.quantity
        product.save()

    order.is_paid = True
    order.save()


    cart.items.all().delete()
    return redirect('shop:order_confirmation', order_id=order.id)

@login_required
@user_passes_test(is_buyer_check, login_url='shop:home')
def order_confirmation_view(request, order_id):
    """Displays a confirmation page for a successfully placed order."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'shop/order_confirmation.html', {'order': order})

# =================
# REVIEW VIEWS
# =================

@require_POST
@login_required
@user_passes_test(is_buyer_check, login_url='shop:home')
def add_review_view(request, product_id):
    """Handles the submission of a new product review."""
    product = get_object_or_404(Product, id=product_id)
    form = ReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.product = product
        review.user = request.user
        review.save()
        return redirect('shop:product_detail', product_id=product.id)
    else:
        # If form is not valid, re-render the detail page with the errors
        reviews = product.reviews.all().order_by('-created_at')
        return render(request, 'shop/product_detail.html', {
            'product': product,
            'reviews': reviews,
            'review_form': form
        })
