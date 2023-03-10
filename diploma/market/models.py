import datetime

from django.contrib.auth.models import Group, User
from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.

class Profile(models.Model):

    ADMIN_STATUS = [
        (True, _('admin')),
        (False, _('user')),
    ]

    ACTIVITY_STATUS = [
        (True, _('Active')),
        (False, _('Not active'))
    ]
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                verbose_name=_('user'))
    admin = models.BooleanField(choices=ADMIN_STATUS,
                                default=False,
                                verbose_name=_('admin status'))
    avatar = models.ImageField(upload_to='avatars/',
                               default=None,
                               blank=True,
                               null=True,
                               verbose_name=_('userPic'))
    status = models.BooleanField(choices=ACTIVITY_STATUS,
                                 default=True,
                                 verbose_name=_('activity status'))
    tel = models.CharField(max_length=10,
                           default=None,
                           verbose_name=_('tel'))

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        if self.admin:
            gr = Group.objects.get(name='Admins')
        else:
            gr = Group.objects.get(name='Users')

        gr.user_set.add(self.user)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')



class Cart(models.Model):
    profile = models.OneToOneField(Profile,
                                   null=False,
                                   on_delete=models.CASCADE,
                                   verbose_name=_('cart'))
    cart_price = models.PositiveIntegerField(default=0,
                                             null=False,
                                             verbose_name=_('price of items in cart'))

    def __str__(self):
        return f'Cart of {self.profile}'

class Item_category(models.Model):
    ACTIVITY_CHOICE = [
        (True, _('Active')),
        (False, _('Not active'))
    ]

    name = models.CharField(null=False,
                            max_length=50,
                            verbose_name=_('category name'))
    status = models.BooleanField(choices=ACTIVITY_CHOICE,
                                 default=True,
                                 null=False,
                                 verbose_name=_('status'))

    def __str__(self):
        return self.name


class Item(models.Model):

    ACTIVITY_CHOICE = [
        (True, _('Active')),
        (False, _('Not active'))
    ]

    name = models.CharField(null=False,
                            max_length=100,
                            verbose_name=_('name'))
    price = models.PositiveIntegerField(null=False,
                                        default=1,
                                        verbose_name=_('price'))
    description = models.TextField(null=False,
                                   default=' ',
                                   verbose_name=_('description'))
    date_created = models.DateTimeField(null=False,
                                        default=datetime.datetime.today(),
                                        verbose_name=_('date added'))
    times_bought = models.PositiveIntegerField(default=0,
                                               null=False,
                                               verbose_name=_('purchase times'))
    status = models.BooleanField(choices=ACTIVITY_CHOICE,
                                 default=True,
                                 null=False,
                                 verbose_name=_('status'))
    category = models.ForeignKey(Item_category,
                                 default=None,
                                 null=True,
                                 on_delete=models.CASCADE)
    has_reviews = models.BooleanField(null=False,
                                      default=False,
                                      verbose_name=_('reviews'))
    number_of_reviews = models.PositiveIntegerField(null=False,
                                                    default=0,
                                                    verbose_name=_('number of reviews'))
    limited = models.BooleanField(null=False,
                                  default=False,
                                  verbose_name=_('limited offer'))

    def __str__(self):
        return self.name



class Item_image(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='item_images/',
                              default=None,
                              verbose_name=_('pic'))

    def __str__(self):
        return f'{self.item} image'


class Item_in_cart(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1,
                                           verbose_name=_('number of items in cart'))

    class Meta:
        verbose_name = _('item_in_cart')
        verbose_name_plural = _('items_in_cart')

    def __str__(self):
        return f'{self.item} in {self.cart}'

    def delete(self, *args, **kwargs):
        cart = Cart.objects.get(id=self.cart.id)
        cart.cart_price -= self.item.price
        cart.save()
        super().delete(*args, **kwargs)


class Item_in_unauthorized_cart(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    session_key = models.TextField(default=None,
                                   verbose_name=_('session key'))
    quantity = models.PositiveIntegerField(default=1,
                                           verbose_name=_('number of items in cart'))

    def __str__(self):
        return f'{self.item} of {self.session_key}'

class Order(models.Model):

    PAYMENT_CHOICE = [
        (_('card'), _('card')),
        (_('random'), _('random')),
    ]

    ACTIVITY_STATUS = [
        (True, _('Active')),
        (False, _('Not active'))
    ]

    DELIVERY_CHOICE = [
        (_('delivery'), _('delivery')),
        (_('in shop'), _('in shop')),
    ]

    profile = models.ForeignKey(Profile,
                                on_delete=models.CASCADE)
    date_of_order = models.DateTimeField(null=False,
                                         default=datetime.datetime.today(),
                                         verbose_name=_('date created'))
    payment_method = models.TextField(choices=PAYMENT_CHOICE,
                                      default='card',
                                      verbose_name=_('payment method'))
    payment_status = models.BooleanField(default=False,
                                         null=False,
                                         verbose_name=_('payment_status'))
    status = models.BooleanField(choices=ACTIVITY_STATUS,
                                 default=True,
                                 null=False,
                                 verbose_name=_('status'))
    delivery_method = models.TextField(choices=DELIVERY_CHOICE,
                                       default='card',
                                       verbose_name=_('delivery method'))
    price = models.PositiveIntegerField(null=False,
                                        default=1,
                                        verbose_name=_('price of order'))
    tel = models.CharField(max_length=10,
                           default=None,
                           verbose_name=_('tel'))
    city = models.TextField(null=True,
                            default=None,
                            verbose_name=_('city'))
    adress = models.TextField(null=True,
                              default=None,
                              verbose_name=_('adress'))
    error = models.TextField(null=True,
                             default=None,
                             verbose_name=_('error'))
    def __str__(self):
        return f'Order id {self.id}'

class Item_in_order(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0,
                                           verbose_name=_('number of items in order'))
    price_of_item = models.PositiveIntegerField(null=False,
                                                default=1,
                                                verbose_name=_('price'))


    def __str__(self):
        return f'Item {self.item.name} in {self.order}'


class Unauthorised_order(models.Model):
    PAYMENT_CHOICE = [
        (_('card'), _('card')),
        (_('random'), _('random')),
    ]

    DELIVERY_CHOICE = [
        (_('delivery'), _('delivery')),
        (_('in shop'), _('in shop')),
    ]

    ACTIVITY_STATUS = [
        (True, _('Active')),
        (False, _('Not active'))
    ]

    session_key = models.TextField(default=None,
                                   verbose_name=_('session key'))
    date_of_order = models.DateTimeField(null=False,
                                         default=datetime.datetime.today(),
                                         verbose_name=_('date created'))
    payment_method = models.TextField(choices=PAYMENT_CHOICE,
                                      default='card',
                                      verbose_name=_('payment method'))
    payment_status = models.BooleanField(default=False,
                                         null=False,
                                         verbose_name=_('payment_status'))
    status = models.BooleanField(choices=ACTIVITY_STATUS,
                                 default=True, null=False,
                                 verbose_name=_('status'))
    delivery_method = models.TextField(choices=DELIVERY_CHOICE,
                                       default='card',
                                       verbose_name=_('delivery method'))
    tel = models.CharField(max_length=10,
                           default=None,
                           verbose_name=_('tel'))
    price = models.PositiveIntegerField(null=False,
                                        default=1,
                                        verbose_name=_('price of order'))
    city = models.TextField(null=True,
                            default=None,
                            verbose_name=_('city'))
    adress = models.TextField(null=True,
                              default=None,
                              verbose_name=_('adress'))
    name = models.TextField(null=True,
                            default=None,
                            verbose_name=_('name'))
    error = models.TextField(null=True,
                             default=None,
                             verbose_name=_('error'))
    def __str__(self):
        return f'Unauth_Order id {self.id}'

class Item_in_unauthorised_order(models.Model):
    item = models.ForeignKey(Item,
                             on_delete=models.CASCADE)
    order = models.ForeignKey(Unauthorised_order,
                              on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0,
                                           verbose_name=_('number of items in order'))
    price_of_item = models.PositiveIntegerField(null=False,
                                                default=1,
                                                verbose_name=_('price'))

    def __str__(self):
        return f'Item {self.item.name} in {self.order}'

class Review(models.Model):
    item = models.ForeignKey(Item,
                             on_delete=models.CASCADE)
    date_created = models.DateField(null=False,
                                    default=datetime.date.today(),
                                    verbose_name=_('date created'))
    description = models.TextField(null=False,
                                   default=' ',
                                   verbose_name=_('description'))
    author = models.ForeignKey(Profile,
                               on_delete=models.CASCADE,
                               default=None, verbose_name=_('author'))
    def save(self, *args, **kwargs):
        if not self.item.has_reviews:
            self.item.has_reviews = True
            self.item.save()
        self.item.number_of_reviews += 1
        self.item.save()
        super().save(*args, **kwargs)


    def delete(self, *args, **kwargs):
        self.item.number_of_reviews -= 1
        if self.item.number_of_reviews == 0:
            self.item.has_reviews = False
        self.item.save()
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = _('review')
        verbose_name_plural = _('reviews')


