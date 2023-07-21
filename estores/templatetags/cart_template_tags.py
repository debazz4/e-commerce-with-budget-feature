from atexit import register
from django import template
from estores.models import Order, Wishlist

register = template.Library()

@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        qs = Order.objects.filter(user=user, ordered=False)
        if qs.exists():
            return qs[0].items.count()
    return 0


@register.filter
def wishlist_item_count(user):
    if user.is_authenticated:
        qs = Wishlist.objects.filter(user=user)
        return qs[0].wished_item.count()
    return 0