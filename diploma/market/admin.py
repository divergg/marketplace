from django.contrib import admin
from django.contrib.sessions.models import Session

from market.models import (Cart, Item, Item_category, Item_image, Item_in_cart,
                           Item_in_order, Item_in_unauthorised_order,
                           Item_in_unauthorized_cart, Order, Profile, Review,
                           Unauthorised_order)

# Register your models here.

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'avatar']
    list_filter = ['user']


@admin.register(Item_category)
class Item_categoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'status']
    list_filter = ['name']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['item', 'date_created', 'description']

class ReviewInline(admin.TabularInline):
    model = Review



class ImagesInline(admin.TabularInline):
    model = Item_image

@admin.register(Item_image)
class Item_imageAdmin(admin.ModelAdmin):
    list_display = ['item', 'image']
    list_filter = ['item']

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'description', 'date_created', 'times_bought', 'status', 'category']
    list_filter = ['name']
    inlines = [ImagesInline, ReviewInline]

class Item_in_orderInline(admin.TabularInline):
    model = Item_in_order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['profile', 'date_of_order', 'payment_method', 'payment_status', 'status', 'tel']
    inlines = [Item_in_orderInline]

@admin.register(Item_in_order)
class Item_in_orderAdmin(admin.ModelAdmin):
    list_display = ['item', 'order', 'quantity', 'price_of_item']


@admin.register(Item_in_cart)
class Item_in_cartAdmin(admin.ModelAdmin):
    list_display = ['item', 'cart', 'quantity']


class Item_in_cartInline(admin.TabularInline):
    model = Item_in_cart


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['profile', 'cart_price']
    inlines = [Item_in_cartInline]


@admin.register(Item_in_unauthorized_cart)
class Item_in_unauthorized_cartAdmin(admin.ModelAdmin):
    list_display = ['item', 'session_key', 'quantity']

@admin.register(Item_in_unauthorised_order)
class Item_in_unauthorised_orderAdmin(admin.ModelAdmin):
    list_display = ['item', 'order', 'quantity', 'price_of_item']

class Item_in_unauthorised_orderInline(admin.TabularInline):
    model = Item_in_unauthorised_order

@admin.register(Unauthorised_order)
class Unauthorised_orderAdmin(admin.ModelAdmin):
    list_display = ['session_key', 'date_of_order', 'payment_method', 'payment_status', 'status', 'tel']
    inlines = [Item_in_unauthorised_orderInline]

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    pass
