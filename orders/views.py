import datetime
import email

from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from cart.models import CartItem
from store.models import Product
from .forms import OrderForm
from orders.models import Order, OrderProduct, Payment
from accounts.models import Account
from django.http import HttpResponse
from django.utils.translation import get_language
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import requests
import datetime
from django.template.loader import render_to_string
from paytm import checksum as paytmchecksum
import json

# Create your views here.


def place_order(request, total=0, quantity=0):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total = total + (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = round(0.12 * total, 2)
    grand_total = tax + total

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.pin_code = form.cleaned_data['pin_code']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            # generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()
            order = Order.objects.get(
                user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
                'order_number': order.order_number
            }
            return render(request, 'orders/payments.html', context)
        else:
            return redirect('checkout')


def payment(request, order_id):
    current_user = request.user
    order = Order.objects.get(
        user=current_user, is_ordered=False, order_number=order_id)
    MERCHANT_KEY = settings.PAYTM_MERCHANT_KEY
    MERCHANT_ID = settings.PAYTM_MERCHANT_ID
    context = {
        'MID': MERCHANT_ID,
        'ORDER_ID': order_id, 'TXN_AMOUNT': str(order.order_total), 'CUST_ID': order.email,
        'INDUSTRY_TYPE_ID': 'Retail', 'WEBSITE': settings.PAYTM_WEBSITE, 'CHANNEL_ID': 'WEB',
        'CALLBACK_URL': 'http://127.0.0.1:8000/orders/response/'
    }
    context['CHECKSUMHASH'] = paytmchecksum.generateSignature(
        context, MERCHANT_KEY)
    return render(request, 'orders/makepayment.html', {'context': context})


@csrf_exempt
def response(request):
    if request.method == "POST":
        MERCHANT_KEY = settings.PAYTM_MERCHANT_KEY
        data_dict = {}
        for key in request.POST:
            data_dict[key] = request.POST[key]
        verify = paytmchecksum.verifySignature(
            data_dict, MERCHANT_KEY, data_dict['CHECKSUMHASH'])
        if verify:
            #data_dict['user'] = request.user
            save_payment_details(data_dict)
            return render(request, "orders/order_complete.html", {"paytm": data_dict})
        else:
            return HttpResponse("checksum verify failed")
    return HttpResponse(status=200)


def save_payment_details(data_dict):
    order = Order.objects.get(
        is_ordered=False, order_number=data_dict['ORDERID'])
    curr_user = Account.objects.filter(email=order.user)
    payment = Payment(
        user=curr_user[0],
        payment_id=data_dict['MID'],
        payment_method=data_dict['PAYMENTMODE'],
        amount_paid=data_dict['TXNAMOUNT'],
        status=data_dict['STATUS']
    )
    payment.save()
    order.payment = payment
    order.is_ordered = True
    order.save()  # Move the cart items to Order Products
    cart_items = CartItem.objects.filter(user=curr_user[0])
    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = curr_user[0].id
        orderproduct.product_id = item.product_id
        orderproduct.product_price = item.product.price
        orderproduct.quantity = item.quantity
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variation.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variation.set(product_variation)
        orderproduct.save()

        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()
    CartItem.objects.filter(user=curr_user[0]).delete()

    mail_subject = 'Thank you! for your order'
    message = render_to_string('orders/order_received_email.html', {
        'user': curr_user[0],
        'order': order,
    })
    to_email = curr_user[0].email
    send_email = EmailMessage(mail_subject, message, to=[to_email, ])
    send_email.send()

# Reduce the quantity of sold product
# Clear cart
# Send order to the customer
# Send order received email to customer
# Send order number and transaction id back to


def order_complete(request):
    return render(request, 'orders/order_complete.html')
