import shlex

import requests.utils

from django.shortcuts import render, redirect, HttpResponse
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from cart.models import Cart, CartItem
from cart.views import _cart_id

# verification
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage


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
            username = email.split("@")[0]
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email,
                                               password=password, username=username)
            user.phone_number = phone_number
            user.save()

            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email, ])
            send_email.send()
            messages.success(
                request, 'Thank you for registering with us. We have sent you a verification email, please verify.')
            return redirect('login')

    form = RegistrationForm()
    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context)


def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)
        if user is not None:
            try:
                # nouser cart
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(
                    cart=cart).exists()
                if is_cart_item_exists:
                    # cart when user is not logged in
                    # All items of nouser cart
                    cart_item = CartItem.objects.filter(cart=cart)
                    cart_item_products = dict()
                    for item in cart_item:
                        cart_item_products[item.product_id] = item

                    cart_item_user = CartItem.objects.filter(user=user)
                    cart_item_user_products = dict()
                    for item in cart_item_user:
                        cart_item_user_products[item.product_id] = item

                    for item, product in cart_item_products.items():
                        if item in cart_item_user_products.keys():
                            variation1 = product.variation.all()
                            lst_var1 = dict()
                            for i in variation1:
                                lst_var1[i.variation_category] = i.variation_value

                            # color:red, size:small
                            variation2 = cart_item_user_products[item].variation.all(
                            )
                            lst_var2 = dict()
                            for i in variation2:
                                lst_var2[i.variation_category] = i.variation_value

                            if len(lst_var1) == len(lst_var2):
                                check = True
                                for key, value in lst_var1.items():
                                    if key in lst_var2.keys():
                                        if value == lst_var2[key] and check:
                                            pass
                                        else:
                                            check = False
                                            product.user = user
                                            product.save()
                                            break
                                if check:
                                    item = CartItem.objects.get(
                                        id=cart_item_user_products[item].id)
                                    item.quantity += 1
                                    item.user = user
                                    item.save()
                            else:
                                check = False
                                product.user = user
                                product.save()
                                break

                        else:
                            product.user = user
                            product.save()

                    # product_variation = []
                    # for item in cart_item:
                    #     variation = item.variation.all()
                    #     product_variation.append(list(variation))
                    #
                    # # user's cart
                    # cart_item = CartItem.objects.filter(user=user)
                    # exist_var_list = []
                    # id = []
                    # for item in cart_item:
                    #     existing_variation = item.variation.all()
                    #     exist_var_list.append(list(existing_variation))
                    #     id.append(item.id)
                    #
                    # for pr in product_variation:
                    #     if pr in exist_var_list:
                    #         index = exist_var_list.index(pr)
                    #         item_id = id[index]
                    #         item = CartItem.objects.get(id=item_id)
                    #         item.quantity += 1
                    #         item.user = user
                    #         item.save()
                    #     else:
                    #         cart_item = CartItem.objects.filter(cart=cart)
                    #         for item in cart_item:
                    #             item.user = user
                    #             item.save()
            except:
                pass
            auth.login(request, user)
            messages.success(request, "You are now logged in.")
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('dashboard')

        else:
            messages.error(request, "Invalid Login Credentials")
            return redirect('login')

    return render(request, 'accounts/login.html')


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, "You are logged out.")
    return redirect('login')


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(
            request, "Congratulations! your account has been activated.")
        return redirect('login')
    else:
        messages.error(request, "Invalid activation link")
        return redirect('register')


@login_required(login_url='login')
def dashboard(request):
    return render(request, 'accounts/dashboard.html')


def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)
            current_site = get_current_site(request)
            mail_subject = 'Reset your password'
            message = render_to_string('accounts/reset_password.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email, ])
            send_email.send()

            messages.success(
                request, "Password reset has been sent to your email address.")
            return redirect('login')

        else:
            messages.error(request, 'Account does not exist.')
            return redirect('forgotPassword')
    return render(request, 'accounts/forgot-password.html')


def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, "Please reset your password.")
        return redirect('resetPassword')
    else:
        messages.error(request, "The link has been expired.")
        return redirect('login')


def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, "Password reset successfully")
            return redirect('login')
        else:
            messages.error(request, "Password don't match.")
            return redirect('resetPassword')
    return render(request, 'accounts/resetPasswordPage.html')
