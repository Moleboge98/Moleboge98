from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone
from datetime import timedelta
from shop.models import User, Order, Store

def is_admin_check(user):
    return user.is_authenticated and user.is_admin()

@user_passes_test(is_admin_check)
def admin_dashboard_view(request):
    total_sales = sum(o.total_price for o in Order.objects.filter(is_paid=True))
    new_users_count = User.objects.filter(date_joined__gte=timezone.now() - timedelta(days=7)).count()
    pending_stores = Store.objects.filter(is_approved=False)

    context = {
        'total_sales': total_sales,
        'new_users_count': new_users_count,
        'pending_stores': pending_stores,
        'all_users': User.objects.all(),
    }
    return render(request, 'shop/admin/dashboard.html', context)
