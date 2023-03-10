from django import template

from market.models import Profile

register = template.Library()

@register.simple_tag(takes_context=True)
def get_profile_id(context):
    request = context['request']
    user = request.user
    if user.is_authenticated:
        profile = Profile.objects.get(user=user)
        return profile.id
