from .models import Category
from carts.models import CartItem,Cart
from store.models import Product
from django.shortcuts import get_object_or_404
from store.views import _get_cart_id

def menu_links(request):
    links = Category.objects.all()
    return dict(links=links)


def counter(request):
    cart_count = 0
    if 'admin' in request.path:
        return {}
    else:
        try:

            cart = Cart.objects.filter(cart_id=_get_cart_id(request))
            if request.user.is_authenticated:
                cart_items = CartItem.objects.all().filter(user = request.user)
            else:
                cart_items = CartItem.objects.all().filter(cart__in=cart)
            for cart_item in cart_items:
                cart_count += cart_item.quantity
        except Cart.DoesNotExist:
            cart_count = 0

    return dict(cart_count=cart_count)
