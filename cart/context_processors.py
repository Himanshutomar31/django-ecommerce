from .models import Cart, CartItem
from .views import _cart_id

def counter(request):
    cart_count = 0
    if 'admin' in request.path:
        return {}
    else:
        try:
            cart = Cart.objects.all().filter(cart_id=_cart_id(request))
            if request.user.is_authenticate:
                cart_items = CartItem.objects.all().filter(cart=cart[:1])
            else:
                cart_items = CartItem.objects.all().filter(user=request.user)
            for cart_item in cart_items:
                cart_count += cart_item.quantity

        except Cart.DoesNotExist:
             cart_count = 0
    return dict(cart_count=cart_count)
