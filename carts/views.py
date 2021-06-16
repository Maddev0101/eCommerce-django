from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from store.models import Product
from .models import Cart,CartItem

from store.models import Variation
# Create your views here.

def _get_cart_id(request):
    cart_id = request.session.session_key
    if not cart_id:
        cart_id = request.session.create()
    return cart_id


def remove_cart(request,product_id,cart_item_id):

    product = get_object_or_404(Product,id=product_id)

    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product,user=request.user,id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_get_cart_id(request))
            cart_item = CartItem.objects.get(product=product,cart=cart,id=cart_item_id)
        if cart_item.quantity >1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except :
        pass
    return redirect('carts:cart')

def remove_cart_item(request,product_id,cart_item_id):

    product = get_object_or_404(Product,id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product,user=request.user,id=cart_item_id)
        cart_item.delete()
    else:
        cart = Cart.objects.get(cart_id=_get_cart_id(request))
        cart_item = CartItem.objects.get(product=product,cart=cart,id=cart_item_id)
        cart_item.delete()
    return redirect('carts:cart')



def cart(request,total=0,quantity=0,cart_items=None):
    try:
        grand_total = 0
        tax = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user,is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_get_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart,is_active=True)

        for cart_item in cart_items:
            total += (cart_item.quantity * cart_item.product.price)
            quantity += cart_item.quantity
        tax = (2*total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass
    context = {'total':total,'quantity':quantity,'cart_items':cart_items,'grand_total':grand_total,'tax':tax}

    return render(request,'carts/cart.html',context)


def add_to_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)
    # if the user is authenticated
    if current_user.is_authenticated:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[item]

                try:
                    variation = Variation.objects.get(product=product,variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except :
                    pass

        cart_item_exists = CartItem.objects.filter(product=product,user=current_user).exists()
        if cart_item_exists:
            cart_item = CartItem.objects.filter(product=product,user=current_user)
            existing_variations_list=[]
            id_list=[]
            for item in cart_item:
                existing_variations = item.variations.all()
                existing_variations_list.append(list(existing_variations))
                id_list.append(item.id)


            if product_variation in existing_variations_list:
                index = existing_variations_list.index(product_variation)
                cart_id = id_list[index]
                cart_item = CartItem.objects.get(product=product,id=cart_id)
                cart_item.quantity +=1
                cart_item.save()

            else:
                cart_item = CartItem.objects.create(product=product,user=current_user,quantity=1)
                if len(product_variation) > 0:
                    cart_item.variations.clear()
                    cart_item.variations.add(*product_variation)
                # cart_item.quantity += 1
                cart_item.save()
        else:
            cart_item = CartItem.objects.create(product=product,user=current_user,quantity=1)
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)

            cart_item.save()

        return redirect ('carts:cart')
    # if the user is not authenticated
    else:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[item]

                try:
                    variation = Variation.objects.get(product=product,variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except :
                    pass

        try:
            cart = Cart.objects.get(cart_id=_get_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=_get_cart_id(request))
            cart.save()

        cart_item_exists = CartItem.objects.filter(product=product,cart=cart).exists()
        if cart_item_exists:
            cart_item = CartItem.objects.filter(product=product,cart=cart)
            existing_variations_list=[]
            id_list=[]
            for item in cart_item:
                existing_variations = item.variations.all()
                existing_variations_list.append(list(existing_variations))
                id_list.append(item.id)


            if product_variation in existing_variations_list:
                index = existing_variations_list.index(product_variation)
                cart_id = id_list[index]
                cart_item = CartItem.objects.get(product=product,id=cart_id)
                cart_item.quantity +=1
                cart_item.save()

            else:
                cart_item = CartItem.objects.create(product=product,cart=cart,quantity=1)
                if len(product_variation) > 0:
                    cart_item.variations.clear()
                    cart_item.variations.add(*product_variation)
                # cart_item.quantity += 1
                cart_item.save()
        else:
            cart_item = CartItem.objects.create(product=product,cart=cart,quantity=1)
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)

            cart_item.save()

        return redirect ('carts:cart')

@login_required
def checkout(request,total=0,quantity=0,cart_items=None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user,is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_get_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart,is_active=True)

        for cart_item in cart_items:
            total += (cart_item.quantity * cart_item.product.price)
            quantity += cart_item.quantity
        tax = (2*total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass
    context = {'total':total,'quantity':quantity,'cart_items':cart_items,'grand_total':grand_total,'tax':tax}
    return render(request,'carts/checkout.html',context)
