import random
import time
from typing import Callable

from market.models import (Cart, Item_in_cart, Item_in_order,
                           Item_in_unauthorised_order,
                           Item_in_unauthorized_cart, Order, Profile,
                           Unauthorised_order)


def check_or_set_user_cookie_data(request):
    if 'session_key' not in request.session:
        request.session['session_key'] = random.getrandbits(128)
    session_key = request.session['session_key']
    return session_key

def get_or_create_items_for_user(request, item, items_num=1):
    session_key = check_or_set_user_cookie_data(request)
    if Item_in_unauthorized_cart.objects.filter(item=item,
                                                session_key=session_key).exists():
        item_in_cart = Item_in_unauthorized_cart.objects.get(item=item,
                                                             session_key=session_key)
        item_in_cart.quantity += items_num
    else:
        item_in_cart = Item_in_unauthorized_cart.objects.create(item=item,
                                                                session_key=session_key)
    item_in_cart.save()

def get_sum_of_items(session_key):
    items = Item_in_unauthorized_cart.objects.filter(session_key=session_key)
    sum = 0
    for item in items:
        sum += item.item.price
    return sum


def create_order_and_cart_data(session_key, cart, profile):
    if Item_in_unauthorized_cart.objects.filter(session_key=session_key).exists():
        items = Item_in_unauthorized_cart.objects.filter(session_key=session_key)
        for item in items:
            Item_in_cart.objects.create(item=item.item,
                                        cart=cart,
                                        quantity=item.quantity)
    if Unauthorised_order.objects.filter(session_key=session_key).exists:
        orders = Unauthorised_order.objects.filter(session_key=session_key)
        for order in orders:
            new_order = Order.objects.create(profile=profile,
                                             date_of_order=order.date_of_order,
                                             payment_method=order.payment_method,
                                             payment_status=order.payment_status,
                                             status=order.status,
                                             tel=order.tel)
            items = Item_in_unauthorised_order.objects.filter(order=order)
            for item in items:
                Item_in_order.objects.create(item=item.item,
                                             order=new_order,
                                             quantity=item.quantity,
                                             price_of_item=item.price_of_item)

def delete_all_items_in_cart(request):
    user = request.user
    if user.is_authenticated:
        profile = Profile.objects.get(user=user)
        cart = Cart.objects.get(profile=profile)
        items = Item_in_cart.objects.filter(cart=cart)
    else:
        session_key = check_or_set_user_cookie_data(request)
        items = Item_in_unauthorized_cart.objects.filter(session_key=session_key)
    for item in items:
        item.delete()


def sleeper(func: Callable) -> Callable:
    '''Декоратор'''
    def wrapper(*args, **kwargs):
        """Функция, останавливающая выполнение передаваемой функции на 5 сек."""
        time.sleep(5)
        result = func(*args, **kwargs)
        return result
    return wrapper

@sleeper
def payment_imitation(number: str):
    if number[0] == '0' or int(number) % 2 == 1:
        return False
    else:
        return True



