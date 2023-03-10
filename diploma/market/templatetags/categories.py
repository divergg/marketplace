from django import template

from market.forms import PriceFilterForm
from market.models import Item_category, Item_image

register = template.Library()

@register.simple_tag
def get_categories():
    categories = Item_category.objects.filter(status=True).order_by('name')
    names = [cat.name for cat in categories]
    return names

@register.simple_tag()
def get_price_filter():
    return PriceFilterForm()

@register.simple_tag(takes_context=True)
def get_user_category_choice(context):
    request = context['request']
    user_choice = request.GET.get('category_query')
    if user_choice:
        category = Item_category.objects.get(name=user_choice)
    else:
        category = Item_category.objects.filter(status=True)[0]
    return category.name


@register.simple_tag(takes_context=True)
def images(context):
    items = context['items']
    images = {}
    for item in items:
        if Item_image.objects.filter(item=item).exists():
            images.update({item: Item_image.objects.filter(item=item)[0]})
    return images



