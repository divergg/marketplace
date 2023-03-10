import datetime
import json
import random
import urllib

from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import (LoginView, LogoutView,
                                       PasswordChangeDoneView,
                                       PasswordChangeView,
                                       PasswordResetCompleteView,
                                       PasswordResetConfirmView,
                                       PasswordResetDoneView,
                                       PasswordResetView)
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext as _
from django.views import View, generic

from market.forms import (AvatarUploadForm, BuyForm, ImageAddForm,
                          Item_categoryForm, ModeratorOrderForm, OrderForm,
                          PaymentForm, ProductForm, ProfileForm,
                          ProfileUpdateForm, RegisterForm, ReviewCreateForm,
                          UnAuthOrderForm, UserUpdateForm)
from market.helpers import (check_or_set_user_cookie_data,
                            create_order_and_cart_data,
                            delete_all_items_in_cart,
                            get_or_create_items_for_user, get_sum_of_items,
                            payment_imitation)
from market.models import (Cart, Item, Item_category, Item_image, Item_in_cart,
                           Item_in_order, Item_in_unauthorised_order,
                           Item_in_unauthorized_cart, Order, Profile, Review,
                           Unauthorised_order, User)

# Create your views here.

class AdminRequiredMixin(object):

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied
        else:
            user_groups = [group.name for group in request.user.groups.all()]
            if 'Admins' not in user_groups:
                raise PermissionDenied
        return super(AdminRequiredMixin, self).dispatch(request, *args, **kwargs)


class UserIsAuthenticatedMixin(object):

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied
        return super(UserIsAuthenticatedMixin, self).dispatch(request, *args, **kwargs)




class MainPageView(View):

    """Choice of category"""

    def get(self, request):


        items = Item.objects.filter(limited=True)[:10]
        context = {
            'items': items
        }
        return render(request, 'market/main.html', context=context)



class ProductList(View):

    template_name = 'market/catalogue.html'

    """Creates a view of items in specific category with filtering
    by price and by reviews options"""
    def get(self, request):
        category_query = request.GET.get('category_query')
        if not category_query:
            category_query = Item_category.objects.filter(status=True)[0]
        category = Item_category.objects.get(name=category_query)
        max_price = request.GET.get('max_price')
        min_price = request.GET.get('min_price')
        if not max_price:
            max_price = 999999999
        if not min_price:
            min_price = 0
        reviews_check = request.GET.get('reviews_check')
        item_query = request.GET.get('item_query')
        if not item_query:
            item_query = ''
        if reviews_check:
            items = Item.objects.filter(Q(name__icontains=item_query)|
                                        Q(description__icontains=item_query),
                                        category=category,
                                        status=True,
                                        price__lte=max_price,
                                        price__gte=min_price,
                                        has_reviews=True)
        else:
            items = Item.objects.filter(Q(name__icontains=item_query)|
                                        Q(description__icontains=item_query),
                                        category=category,
                                        status=True,
                                        price__lte=max_price,
                                        price__gte=min_price)

        serialized_items = serializers.serialize('json', items)
        serialized_category = category.name
        context = {'items': items,
                   'category': category,
                   'serialized_items': serialized_items,
                   'serialized_category': serialized_category}
        return render(request, self.template_name, context=context)

    def post(self, request):
        """
        Does filtering of products, allows to add item to a cart
        """

        items = urllib.parse.unquote(request.POST.get('items_data'))
        items = json.loads(items)
        item_ids = [item['pk'] for item in items]
        items = Item.objects.filter(id__in=item_ids)
        sort_type = request.POST.get('sort_query')
        if sort_type == 'Price':
            items = items.order_by('price')
        else:
            items = items.order_by('name')
        category = request.POST.get('category_data')
        if request.POST.get('add_to_cart'):
            new_item_added = int(request.POST.get('item_added'))
            new_item_added = Item.objects.get(id=new_item_added)
            if request.user.is_authenticated:
                profile = Profile.objects.get(user=request.user)
                cart = Cart.objects.get(profile=profile)
                item_added = Item_in_cart.objects.filter(item=new_item_added, cart=cart).exists()
                if item_added:
                    new_item_added = Item_in_cart.objects.get(item=new_item_added, cart=cart)
                    new_item_added.quantity += 1
                    new_item_added.save()
                else:
                    new_item_added = Item_in_cart.objects.create(item=new_item_added, cart=cart, quantity=1)
                cart.cart_price += new_item_added.item.price
                cart.save()
            else:
                get_or_create_items_for_user(request, new_item_added)
        serialized_category = category
        category = Item_category.objects.get(name=category)
        serialized_items = serializers.serialize('json', items)
        context = {'items': items,
                   'category': category,
                   'serialized_items': serialized_items,
                   'serialized_category': serialized_category}
        return render(request, self.template_name, context=context)



class ProductDetail(generic.DetailView):

    """ Generates detail view of a product, allows adding to
    a Cart and writing a Review to the product"""

    model = Item
    template_name = 'market/product.html'
    context_object_name = 'item'

    def get_context_data(self, rev_num=3, **kwargs):
        context = super().get_context_data(**kwargs)
        item = self.get_object()
        reviews = Review.objects.filter(item=item)
        images = Item_image.objects.filter(item=item)
        context['buy_form'] = BuyForm()
        context['review_form'] = ReviewCreateForm()
        context['images'] = images
        length = len(reviews)
        if rev_num < length:
            rev_add = True
        else:
            rev_add = False
        context['rev_add'] = rev_add
        context['rev_num'] = rev_num
        if reviews.exists():
            review_exists = True
            context['reviews'] = reviews[0:rev_num]
        else:
            review_exists = False
            context['reviews'] = _('There are no reviews yet')
        context['reviews_exist'] = review_exists
        return context

    def post(self, request, pk):
        """
        Add product in cart or add review
        """
        item = self.get_object()
        user = self.request.user
        review_form = ReviewCreateForm(request.POST)
        if review_form.is_valid():
            if user.is_authenticated:
                profile = Profile.objects.get(user=user)
                description = review_form.cleaned_data['description']
                review = Review.objects.create(item=item, description=description, author=profile)
                review.save()
                return HttpResponseRedirect(f'/catalogue/{pk}')
            else:
                raise PermissionDenied
        buy_form = BuyForm(request.POST)
        if buy_form.is_valid():
            items_num = buy_form.cleaned_data['number']
            price = item.price
            if user.is_authenticated:
                profile = Profile.objects.get(user=user)
                cart = Cart.objects.get(profile=profile)
                if Item_in_cart.objects.filter(item=item, cart=cart).exists():
                    item_in_cart = Item_in_cart.objects.get(cart=cart, item=item)
                else:
                    item_in_cart = Item_in_cart.objects.create(cart=cart, item=item)
                item_in_cart.quantity += items_num - 1
                cart.cart_price += price * float(items_num)
                item_in_cart.save()
                cart.save()
                return HttpResponseRedirect(f'/catalogue/{pk}')
            else:
                get_or_create_items_for_user(request, item, items_num)
                return HttpResponseRedirect(f'/catalogue/{pk}')
        rev_new = request.POST['number_of_reviews']
        if rev_new:
            rev_new += 3
            self.object = self.get_object()
            context = self.get_context_data(rev_num=rev_new)
            return render(request, self.template_name, context=context)
        return HttpResponseRedirect(f'/catalogue')


class CartView(View):

    """View of profile's cart with edition options"""

    template = 'market/cart.html'

    def get(self, request):
        user = request.user
        if user.is_authenticated:
            profile = Profile.objects.get(user=user)
            cart = Cart.objects.get(profile=profile)
            check_cart_full = False
            if Item_in_cart.objects.filter(cart=cart).exists():
                check_cart_full = True
            items_in_cart = Item_in_cart.objects.filter(cart=cart)
            price = cart.cart_price
        else:
            check_cart_full = False
            session_key = check_or_set_user_cookie_data(request)
            if Item_in_unauthorized_cart.objects.filter(session_key=session_key).exists():
                check_cart_full = True
            items_in_cart = Item_in_unauthorized_cart.objects.filter(session_key=session_key)
            price = get_sum_of_items(session_key)
        return render(request, self.template, context={
            'items_in_cart': items_in_cart,
            'price': price,
            'check_cart_full': check_cart_full,
        })


    def post(self, request):
        """
        Delete a product or change a quantity of products
        """
        user = request.user
        pk = request.POST['id']
        if user.is_authenticated:
            item = Item_in_cart.objects.get(id=pk)
            profile = Profile.objects.get(user=user)
            cart = Cart.objects.get(profile=profile)
        else:
            item = Item_in_unauthorized_cart.objects.get(id=pk)
        if request.POST.get('delete'):
            item.delete()
        elif request.POST.get('add_more'):
            add = int(request.POST['add_more'])
            item.quantity += add
            item.save()
            price = item.quantity * item.item.price
            if user.is_authenticated:
                cart.cart_price += price
                cart.save()
        elif request.POST.get('del_more'):
            reduce = int(request.POST['del_more'])
            if item.quantity - reduce <= 0:
                item.delete()
            else:
                item.quantity -= reduce
                item.save()
                price = item.quantity * item.item.price
                if user.is_authenticated:
                    cart.cart_price -= price
                    cart.save()
        return HttpResponseRedirect('/cart')

class OrderView(View):

    """Confirm an order view"""

    template = 'market/order.html'

    def get(self, request):
        user = request.user
        if user.is_authenticated:
            profile = Profile.objects.get(user=user)
            cart = Cart.objects.get(profile=profile)
            if not Item_in_cart.objects.filter(cart=cart).exists():
                raise PermissionDenied
            items = Item_in_cart.objects.filter(cart=cart)
            order = Order.objects.create(profile=profile, tel=profile.tel)
            for item in items:
                Item_in_order.objects.create(item=item.item,
                                             order=order,
                                             quantity=item.quantity,
                                             price_of_item=item.item.price)
            items_in_order = Item_in_order.objects.filter(order=order)
            order.tel = profile.tel
            order.name = profile.user.username
            order.save()
        else:
            profile = None
            session_key = check_or_set_user_cookie_data(request)
            if not Item_in_unauthorized_cart.objects.filter(session_key=session_key):
                raise PermissionDenied
            items = Item_in_unauthorized_cart.objects.filter(session_key=session_key)
            order = Unauthorised_order.objects.create(session_key=session_key, tel='0')
            for item in items:
                Item_in_unauthorised_order.objects.create(item=item.item,
                                                          order=order,
                                                          quantity=item.quantity,
                                                          price_of_item=item.item.price)
            items_in_order = Item_in_unauthorised_order.objects.filter(order=order)
        order_form = OrderForm()
        price = 0
        for item in items_in_order:
            price += item.price_of_item
        order.price = price
        order.save()
        context = {
            'items_in_order': items_in_order,
            'order_form': order_form,
            'price': price,
            'profile': profile,
            'order_id': order.id,
            'order': order
        }
        return render(request, self.template, context=context)

    def post(self, request):
        """ Create an order and proceed to payment"""
        user = request.user
        tel = request.POST['tel']
        order_form = OrderForm(request.POST)
        if order_form.is_valid():
            payment_method = request.POST['payment_method']
            delivery_method = request.POST['delivery_method']
            address = request.POST['address']
            order_id = request.POST['order_id']
            if user.is_authenticated:
                order = Order.objects.get(id=order_id)
                kwarg = order_id
            else:
                session_key = check_or_set_user_cookie_data(request)
                order = Unauthorised_order.objects.get(session_key=session_key)
                order.name = request.POST['enter_name']
                kwarg = session_key
            order.tel = tel
            order.delivery_method = delivery_method
            order.payment_method = payment_method
            order.adress = address
            order.save()
            url = reverse('payment', kwargs={'pk': kwarg})
            return HttpResponseRedirect(url)
        return HttpResponseRedirect('order')



class PaymentView(View):

    template = 'market/payment.html'

    def get(self, request, pk):
        if request.user.is_authenticated:
            order = Order.objects.get(id=pk)
        else:
            order = Unauthorised_order.objects.get(session_key=pk)
        payment_method = order.payment_method
        delivery_method = order.delivery_method
        random_button = False
        random_num = None
        if payment_method == 'random':
            random_button = True
            if request.GET.get('random_card'):
                random_num = random.randint(10000000, 99999999)
        payment_form = PaymentForm()

        if delivery_method == 'delivery':
            order.price += 200
        context = {
            'random_button': random_button,
            'payment_form': payment_form,
            'order': order,
            'random_num': random_num,
            'param': pk
        }
        return render(request, self.template, context=context)

    @transaction.atomic()
    def post(self, request, pk):
        """immitation of payment"""
        if request.user.is_authenticated:
            order = Order.objects.get(id=pk)
        else:
            order = Unauthorised_order.objects.get(session_key=pk)
        payment_method = order.payment_method
        confirm = False
        if payment_method == 'card':
            form = PaymentForm(request.POST)
            if form.is_valid():
                confirm = True
                card_num = request.POST['card_num']
        else:
            confirm = True
            card_num = request.POST['random_num']
        if confirm:
            url1 = reverse('confirmation', kwargs={'pk': pk})
            url2 = reverse('error', kwargs={'pk': pk})
            imit = payment_imitation(card_num)
            if imit:
                order.payment_status = True
                order.error = None
                order.save()
                delete_all_items_in_cart(request)
                return HttpResponseRedirect(url1)
            else:
                order.error = 'Payment is failed. Incorrect account data'
                order.save()
                return HttpResponseRedirect(url2)

class PaymentConfirmationView(View):

    template = 'market/confirmation.html'
    def get(self, request, pk):
        context = {
            'param': pk
        }
        return render(request, self.template, context=context)


class PaymentErrorView(View):
    template = 'market/error.html'
    def get(self, request, pk):
        context = {
            'param': pk
        }
        return render(request, self.template, context=context)

class AccountDetailView(UserIsAuthenticatedMixin, generic.DetailView):
    template_name = 'market/account.html'
    model = User
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        context = super(AccountDetailView, self).get_context_data()
        user = self.get_object()
        profile = Profile.objects.get(user=user)
        orders = Order.objects.filter(profile=profile).order_by('date_of_order')
        context['profile'] = profile
        context['orders'] = orders
        return context


class AccountUpdateView(UserIsAuthenticatedMixin, generic.UpdateView):
    model = User
    form_class = UserUpdateForm
    context_object_name = 'user'
    template_name = 'market/profile.html'

    def get_success_url(self):
        success_url = reverse_lazy('account', kwargs={'pk': self.get_object().id})
        return success_url

    def get(self, request, *args, **kwargs):

        return super().get(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super(AccountUpdateView, self).get_context_data()
        user = self.get_object()
        profile = Profile.objects.get(user=user)
        profile_form = ProfileUpdateForm()
        context['profile'] = profile
        context['avatar_form'] = AvatarUploadForm()
        context['profile_form'] = profile_form
        return context

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        profile = Profile.objects.get(user=user)
        avatar_form = AvatarUploadForm(request.POST)
        if avatar_form.is_valid():
            profile.avatar = request.FILES.get('image')
            profile.save()
        profile_form = ProfileUpdateForm(request.POST)
        if profile_form.is_valid():
            profile.tel = profile_form.cleaned_data['tel']
            profile.save()
        return super().post(self, request, *args, **kwargs)


class PasswordUpdateView(PasswordChangeView):
    template_name = 'market/password_change.html'
    success_url = reverse_lazy('password_change_done')
    form_class = PasswordChangeForm


class PasswordUpdateDone(PasswordChangeDoneView):
    template_name = 'market/password_change_done.html'



class OrderHistoryView(View):

    template = 'market/history.html'

    def get(self, request, pk, sk):
        profile = Profile.objects.get(id=pk)
        order = Order.objects.get(id=sk)
        if profile != order.profile:
            raise PermissionDenied
        payment_status = order.payment_status
        items = Item_in_order.objects.filter(order=order)
        context = {
            'order': order,
            'payment_status': payment_status,
            'items': items,
            'profile': profile
        }
        return render(request, self.template, context=context)

    def post(self, request):
        """ Change an order"""
        pass


class SiteLoginView(LoginView):
    template_name = 'market/sign_in.html'


class SiteLogoutView(LogoutView):
    template_name = 'market/sign_out.html'


class RegisterView(View):

    template = 'market/sign_up.html'

    def get(self, request):
        form = RegisterForm()
        return render(request, self.template, context={'form': form})

    def post(self, request):
        """ Register of a new user"""

        form = RegisterForm(request.POST)
        if form.is_valid():
            tel = form.cleaned_data['tel']
            user = form.save()
            profile = Profile.objects.create(
                user=user,
                tel=tel
            )
            username = form.cleaned_data.get('username')
            pass_w = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=pass_w)
            login(request, user)
            cart = Cart.objects.create(profile=profile)
            session_key = check_or_set_user_cookie_data(request)
            create_order_and_cart_data(session_key, cart, profile)
            return HttpResponseRedirect('/')
        return render(request, self.template, context={'form': form})


class UserPasswordResetView(PasswordResetView):
    template_name = 'password_reset/password_reset_form.html'
    subject_template_name = "password_reset/password_reset_subject.txt"
    email_template_name = "password_reset/password_reset_email.html"

class UserPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'password_reset/password_reset_complete.html'

class UserPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'password_reset/password_reset_done.html'


class UserPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'password_reset/password_reset_confirm.html'


class ModeratorsView(AdminRequiredMixin, View):

    template_name = 'market/moderator.html'

    def get(self, request):
        return render(request, self.template_name)


class UsersListView(AdminRequiredMixin, generic.ListView):

    template_name = 'market/moderator_users.html'
    model = Profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profiles'] = Profile.objects.all()
        return context

    def post(self, request):
        search = request.POST.get('searcher')
        if search or search == '':
            users = User.objects.filter(username__icontains=search)
            ids = [user.id for user in users]
            profiles = Profile.objects.filter(user__in=ids)
            return render(request, self.template_name, context={'profiles': profiles})

class OrdersListView(AdminRequiredMixin, generic.ListView):
    template_name = 'market/moderator_orders.html'
    model = Order
    context_object_name = 'orders'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unauth_orders'] = Unauthorised_order.objects.all()
        return context


    def post(self, request):
        search = request.POST.get('searcher')
        if search or search == '':
            users = User.objects.filter(username__icontains=search)
            tels = Profile.objects.filter(tel__icontains=search)
            ids = [user.id for user in users]
            profiles = Profile.objects.filter(user__in=ids)
            orders = Order.objects.filter(profile__in=profiles)
            unauth_orders = Unauthorised_order.objects.filter(tel__in=tels)
            return render(request, self.template_name, context={'orders': orders, 'unauth_orders': unauth_orders})

class ProductsListView(AdminRequiredMixin, generic.ListView):
    template_name = 'market/moderator_products.html'
    model = Item

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = Item.objects.filter(status=True)
        return context

    def post(self, request):
        search = request.POST.get('searcher')
        if search or search == '':
            items = Item_category.objects.filter(name__icontains=search, status=True)
            return render(request, self.template_name, context={'items': items})
        pk = request.POST['id']
        item = Item.objects.get(id=pk)
        if request.POST.get('Delete'):
            item.status = False
        item.save()
        return HttpResponseRedirect('/moderator_products')


class CategoriesListView(AdminRequiredMixin, generic.View):

    template_name = 'market/moderator_categories.html'
    #model = Item_category

    def get(self, request):
        categories = Item_category.objects.filter(status=True).all()
        context = {
            'categories' : categories,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        """ Change a category or add a new one"""
        search = request.POST.get('searcher')
        if search or search == '':
            category = Item_category.objects.filter(name__icontains=search, status=True)
            return render(request, self.template_name, context={'categories': category})
        pk = request.POST['id']
        category = Item_category.objects.get(id=pk)
        new_name = request.POST['name']
        if request.POST.get('Delete'):
            category.status = False
        if new_name:
            category.name = new_name
        category.save()
        return HttpResponseRedirect('/moderator_categories')





class UsersUpdateView(AdminRequiredMixin, generic.UpdateView):
    model = Profile
    form_class = ProfileForm
    context_object_name = 'profile'
    template_name = 'market/moderator_users_edit.html'
    success_url = reverse_lazy("moderator_users")


class OrdersUpdateView(AdminRequiredMixin, generic.UpdateView):
    model = Order
    form_class = ModeratorOrderForm
    context_object_name = 'order'
    template_name = 'market/moderator_orders_edit.html'
    success_url = reverse_lazy("moderator_orders")

class UnAuthOrdersUpdateView(AdminRequiredMixin, generic.UpdateView):
    model = Unauthorised_order
    form_class = UnAuthOrderForm
    context_object_name = 'order'
    template_name = 'market/moderator_unauth_orders_edit.html'
    success_url = reverse_lazy("moderator_orders")

class ProductUpdateView(AdminRequiredMixin, generic.UpdateView):
    model = Item
    form_class = ProductForm
    context_object_name = 'product'
    template_name = 'market/moderator_products_edit.html'
    success_url = reverse_lazy('moderator_products')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['image_form'] = ImageAddForm
        if Item_image.objects.filter(item=self.get_object()).exists():
            context['images'] = Item_image.objects.filter(item=self.get_object())
        else:
            context['images'] = None
        return context

    def post(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)
        item = self.get_object()
        image_form = ImageAddForm(request.POST)
        if image_form.is_valid():
            images = request.FILES.getlist('image')
            for ims in images:
                Item_image.objects.create(item=item, image=ims)
            return HttpResponseRedirect('/moderator_products')
        return HttpResponseRedirect('/moderator_products_edit.html')


class CategoriesDetailView(AdminRequiredMixin, generic.DetailView):
    model = Item_category
    template_name = 'market/moderator_categories_edit.html'
    context_object_name = 'category'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = Item.objects.filter(category=self.get_object(), status=True)
        return context


    def post(self, request, pk):
        search = request.POST.get('searcher')
        if search or search == '':
            item = Item.objects.filter(name__icontains=search, status=True, category=self.get_object())
            return render(request, self.template_name, context={'items': item})
        item = Item.objects.get(id=pk)
        if request.POST.get('Delete'):
            item.category = None
            item.save()
        return HttpResponseRedirect(f'/moderator_categories/{pk}')


class ProductCreateView(AdminRequiredMixin, generic.CreateView):
    model = Item
    form_class = ProductForm
    template_name = 'market/moderator_products_create.html'
    context_object_name = 'product'
    success_url = reverse_lazy("moderator_products")


class CategoryCreateView(AdminRequiredMixin, generic.CreateView):
    model = Item_category
    form_class = Item_categoryForm
    template_name = 'market/moderator_categories_create.html'
    context_object_name = 'category'
    success_url = reverse_lazy("moderator_categories")

