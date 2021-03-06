from django.shortcuts import render,HttpResponse,redirect
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from .forms import RegistrationForm
from .models import Account
from carts.models import Cart,CartItem
from carts.views import _get_cart_id

import requests

# Create your views here.

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            username = email.split('@')[0]

            user = Account.objects.create(
            first_name=first_name,
            last_name = last_name,
            email = email,
            username = username,
            )
            user.set_password(password)
            user.phone_number = phone_number
            user.save()
            #user activation
            current_site = get_current_site(request)
            mail_subject = "Account Activation"
            message = render_to_string('accounts/verification_email.html',{
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user)
            })
            to_email = email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()

            # messages.success(request,'Thank you for registering with us, please check your inbox for verification email')
            return redirect('/accounts/login/?command=verification&email='+email)
    else:
        form = RegistrationForm()
    context = {'form':form}

    return render(request,'accounts/register.html',context)


def user_login(request):
    if request.method =='POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, password=password, username=email)
        if user:
            try:
                cart = Cart.objects.get(cart_id=_get_cart_id(request))
                cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)
                    #getting the product variations by cart id
                    product_variations = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variations.append(list(variation))

                    #get the cart items from the user to access its product variations
                    if cart_item_exists:
                        cart_item = CartItem.objects.filter(user=user)
                        existing_variations_list=[]
                        id_list=[]
                        for item in cart_item:
                            existing_variations = item.variations.all()
                            existing_variations_list.append(list(existing_variations))
                            id_list.append(item.id)
                        for product_variation in product_variations:
                            if product_variation in existing_variations_list:
                                index = existing_variations_list.index(product_variation)
                                item_id = id_list[index]
                                item = CartItem.objects.get(id=item_id)
                                item.quantity +=1
                                item.user = user
                                item.save()
                            else:
                                cart_item = CartItem.objects.filter(cart=cart)
                                for item in cart_item:
                                    item.user = user
                                    item.save()
            except:
                pass
            login(request,user)
            messages.success(request,'You are now logged in')
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    next_page = params['next']
                    return redirect(next_page)
            except:
                return redirect('accounts:dashboard')
        else:
            messages.error(request,'Invalid Login Credentials')
            return redirect('accounts:login')

    return render(request,'accounts/login.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('home')


def activate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None
    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request,'Your account is now activated')
        return redirect('accounts:login')
    else:
        messages.error(request,'Invalid Activation Link')
        return redirect('accounts:register')

@login_required
def dashboard(request):
    return render(request,'accounts/dashboard.html')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)
            current_site = get_current_site(request)
            mail_subject = "Reset Password"
            message = render_to_string('accounts/reset_pass_email.html',{
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user)
            })
            to_email = email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()
            messages.success(request,'Reset Password Email Has Been Sent')
            return redirect('accounts:login')

        else:
            messages.error(request,'Account Does Not Exist')
            return redirect('accounts:forgot_password')

    return render(request,'accounts/forgot_password.html')


def reset_password_validate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None
    if user and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        return redirect('accounts:reset_password')
    else:
        messages.error(request,'This link has been expired')
        return redirect('accounts:login')


def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,'Your Password Has Been Reset!')
            return redirect('accounts:login')
        else:
            messages.error(request,'Passwords do not match')
            return redirect('accounts:reset_password')
    else:
        return render(request,'accounts/reset_password.html')
