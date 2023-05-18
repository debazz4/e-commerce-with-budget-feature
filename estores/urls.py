from ast import Or
from audioop import add
from typing import OrderedDict
from unicodedata import name
from django.urls import path
from .views import (HomeView, 
                    ItemDetailView,
                    OrderSummaryView,
                    CheckoutView,
                    PaymentView,
                    AddCouponView,
                    Dashboard,
                    Shipping_Option,
                    SearchView,
                    add_to_cart, remove_from_cart,
                    signup, loginPage, 
                    logoutUser, remove_single_item_from_cart,
                    add_single_item_to_cart,

                    )



app_name = 'estores'

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', loginPage, name='login'),
    path('logout/', logoutUser, name='logout'),

    path('', HomeView.as_view(), name='home'),
    path('search/', SearchView.as_view(), name='search'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart, name='remove-single-item-from-cart'),
    path('add-item-to-cart/<slug>/', add_single_item_to_cart, name='add-single-item-to-cart'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
    path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('shipping-option/', Shipping_Option.as_view(), name='shipping-option'),
    path('dashboard/', Dashboard.as_view(), name='dashboard'),
]