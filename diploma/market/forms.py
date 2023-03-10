from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import MaxValueValidator
from django.utils.translation import gettext_lazy as _

from market.models import (Item, Item_category, Order, Profile, Review,
                           Unauthorised_order, User)


class AuthForm(forms.Form):
    username = forms.CharField(max_length=30, label=_('Username'))
    password = forms.CharField(max_length=30,
                               widget=forms.PasswordInput,
                               label=_('Password'))


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=50,
                                 required=True,
                                 label=_('First name'))
    last_name = forms.CharField(max_length=50,
                                required=True,
                                label=_('Last name'))
    tel = forms.CharField(max_length=10,
                          required=True,
                          label=_('Tel'),
                          widget=forms.TextInput(attrs={'placeholder': "9001234567",
                                                 'pattern': "(^9)([0-9]{9})"}))
    email = forms.EmailField(max_length=40,
                             required=True,
                             label=_('Email'))




class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = '__all__'
        exclude = ('user', 'admin')


class ModeratorOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = '__all__'


class UnAuthOrderForm(forms.ModelForm):

    class Meta:
        model = Unauthorised_order
        fields = '__all__'


class ProductForm(forms.ModelForm):

    class Meta:
        model = Item
        fields = '__all__'
        exclude = ('times_bought', )

class Item_categoryForm(forms.ModelForm):

    class Meta:
        model = Item_category
        fields = '__all__'


class ImageAddForm(forms.Form):
    image = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={'multiple': True}),
        required=False,
        label=_('Image'))

class BuyForm(forms.Form):
    number = forms.DecimalField(max_digits=2,
                                decimal_places=0,
                                label=_('Quantity of items'),
                                required=True,
                                min_value=0,
                                initial=1)


class PriceFilterForm(forms.Form):
    min_price = forms.DecimalField(max_digits=8,
                                    decimal_places=0,
                                    label=_('Min price'),
                                    required=False,
                                    min_value=0
                                    )
    max_price = forms.DecimalField(max_digits=8,
                                   decimal_places=0,
                                   label=_('Max price'),
                                   required=False,
                                   max_value=99999999)

class ReviewCreateForm(forms.ModelForm):

    class Meta:
        model = Review
        fields = ('description',)


class UserUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class ProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ('tel',)
        widgets = {'tel': forms.TextInput(attrs={'placeholder': "9001234567",
                                                 'pattern': "(^9)([0-9]{10})"})}


class AvatarUploadForm(forms.Form):
    image = forms.ImageField(
        required=False,
        label=_('Avatar'))




class OrderForm(forms.Form):
    payment_method = forms.ChoiceField(choices= [
        (_('card'), _('card')),
        (_('random'), _('random'))
    ],
        required=True)
    delivery_method = forms.ChoiceField(choices= [
        (_('delivery'), _('delivery')),
        (_('in shop'), _('in shop'))
    ],
        required=True)
    address = forms.CharField(widget=forms.TextInput())


def is_even(value):
    if value % 2 != 0:
        raise forms.ValidationError(_('Please enter an even number.'))
class PaymentForm(forms.Form):
    card_num = forms.IntegerField(required=True,
                                  validators=[is_even, MaxValueValidator(99999999)],
                                  widget=forms.TextInput(attrs={'placeholder': "12345678",
                                                             'pattern': "[0-9]{8}"}))