import imp
from pickle import LIST
from re import template
import re
from tabnanny import check
from webbrowser import get
from django.conf import settings
from django.contrib import messages
from django.db.models import Q, F
from datetime import datetime
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, View,TemplateView
from django.views.generic.edit import FormMixin
from django.shortcuts import redirect
from django.urls import reverse
from .forms import (SignUpForm, CheckoutForm, CouponForm, Shipping, 
                    RefundForm, PaymentForm, ReviewForm, BudgetForm)
from django.utils import timezone
from django.db.models import Avg, Count
from django.db.models.functions import Now
from .models import (Item, Order, OrderItem, Address, UserProfile, Refund, 
                     Coupon, Payment, Wishlist, ProductReview, Budgets, CATEGORY_CHOICES)
import stripe
import string
import random

stripe.api_key = settings.STRIPE_SECRET_KEY

def delete_expired_budget():
    Budgets._base_manager.filter(duration__lte=Now()).delete()

def create_ref_code():
                return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))



class HomeView(ListView):
    model = Item
    template_name = "home.html"
    paginate_by = 12
    #ordering = ['-price']  # Default ordering when no sort_by parameter is provided

    
    def get_queryset(self):
        queryset = super().get_queryset()  # Default ordering when an invalid sort_by parameter is provided
        sort_by = self.request.GET.get('sort_by', '-price')
        if sort_by == 'price_asc':
            queryset = Item.objects.order_by('price')
        elif sort_by == 'price_desc':
            queryset = Item.objects.order_by('-price')
        elif sort_by == 'discount_asc':
            queryset = Item.objects.order_by('discount_price')
        elif sort_by == 'discount_desc':
            queryset = Item.objects.order_by('-discount_price')
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = CATEGORY_CHOICES
        category_counts = Item.objects.values('category').annotate(count=Count('category'))
        context['category_counts'] = category_counts
        #context['page_request'] = self.page_request
        return context
    
    
    


    
class ItemDetailView(FormMixin, DetailView):
    model = Item,
    template_name = "products.html"
    context_object_name = 'review'
    form_class = ReviewForm
    id = Item.objects.only('id')

    #def get_context_data(self, **kwargs):
   #     context = super().get_context_data(**kwargs)
    #    context['form'] = ReviewForm()  # Add the form to the context
     #   return context

    def form_valid(self, form):
        item = get_object_or_404(Item, id=self.kwargs.get('pk'))
        review = form.save(commit=False)
        review.item = item
        review.save()
        return super().form_valid(form)
    
    def get_success_url(self):
         return reverse('product', args=[self.kwargs.get('pk')])

def productDetail(request, slug):
    product = Item.objects.get(slug=slug)
    related_item = Item.objects.filter(category=product.category).exclude(slug=slug)[:5]
    #review = ProductReview.objects.all()
    form = ReviewForm(request.POST)

    #Check 
    canAdd = True
    if request.user.is_authenticated:
        reviewCheck = ProductReview.objects.filter(user=request.user, product=product).count()
        if request.user.is_authenticated:
            if reviewCheck > 0:
                canAdd = False
    # End check

    #Fetch reviews
    reviews = ProductReview.objects.filter(product=product)
    #End

    #Fetch avg rating
    avg_reviews = ProductReview.objects.filter(product=product).aggregate(avg_rating=Avg('review_rating'))
    #End
    context = {
        'product': product,
        'related_item': related_item,
        'form': form,
        'canAdd': canAdd,
        'reviews': reviews,
        'avg_reviews': avg_reviews,
        
    }
    return render(request, "products.html",context)

class SearchView(ListView):
    model = Item
    template_name = "search.html" 
    #queryset = Item.objects.filter(title__icontains='Bag')

    def get_queryset(self):
        #    try:
        query= self.request.GET.get('q')
        if (query != None):
            object_list = Item.objects.filter(Q(title__icontains=query))
            return object_list
        else:
            return (self.request,  "Please enter a keyword for search to serve you better")
        #    except:
        #        return (self.request, "The product you are looking for is not av5ailable yet!")

class SortView(ListView):
    model = Item
    template_name = "sort.html" 
    #queryset = Item.objects.filter(title__icontains='Bag')

    def get_queryset(self):
        #    try:
        sort_by = self.request.GET.get("sort","l2h")
        if sort_by == "l2h":
            object_list = Item.objects.order_by("price")
            return object_list
        elif sort_by == "h2l":
            object_list = Item.objects.order_by("-price")
            return object_list
        elif sort_by == "d":
            object_list = Item.objects.order_by("discount_price")
            return object_list

            #return (self.request,  "Please enter a keyword for search to serve you better")

def searchitem(request):
    if request.method == 'GET':
        query= request.GET.get('q')

        #submitbutton= request.GET.get('submit')

        if query is not None:
            lookups= Q(title__icontains=query) | Q(price__icontains=query)

            results= Item.objects.filter(lookups).distinct()

            context={'results': results,
                     #'submitbutton': submitbutton
                     }

            return render(request, 'search.html', context)

        else:
            return render(request, 'search.html')

    else:
        return render(request, 'search.html')

class Dashboard(LoginRequiredMixin, TemplateView):
    def get(self, *args, **kwargs):
        order = Order.objects.filter(user=self.request.user, ordered=True)
        form = BudgetForm()
        b_address = Address.objects.get(user=self.request.user, address_type='B', default=True)
        s_address = Address.objects.get(user=self.request.user, address_type='S', default=True)
        try:
            budget = Budgets.objects.get(user=self.request.user or None)
        except Budgets.DoesNotExist:
             budget = None
        #matches = order | b_address | s_address | budget
        total = 0
        for orders in order:
            total += orders.get_total_add_shipping() 
        print(total)
        context = {
            'order' : order,
            'b_address' : b_address,
            's_address' : s_address,
            'form' : form,
            'budget' : budget,

        }
        return render(self.request, 'dashboard.html', context)
    
    def post(self, *args, **kwargs):
        form = BudgetForm(self.request.POST or None)
        if form.is_valid():
            try:
                budget_name = form.cleaned_data.get('budget_name')
                amount = form.cleaned_data.get('amount')
                duration = form.cleaned_data.get('duration')


                budget = Budgets()
                budget.user = self.request.user
                budget.budget_name = budget_name
                budget.amount = amount
                budget.duration = duration
                
                budget.save()
                messages.success(self.request, "Successfully added budget")
                return redirect("estores:dashboard")
            except ObjectDoesNotExist:
                messages.info(self.request, "You have not enter necessary conditions for budget")
                return redirect("estores:dashboard")

class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                    
                    'object' : order,
                    'couponform': CouponForm(),
                    'DISPLAY_COUPON_FORM': True,
                }
            
            return render(self.request, 'cart.html', context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect('estores:home')
                                
def is_valid_form(values):
                valid = True
                for field in values:
                    if field == '':
                        valid = False
                return valid


class CheckoutView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'order': order,
                
            }

            shipping_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='S',
                default=True
            )
            if shipping_address_qs.exists():
                context.update(
                    {'default_shipping_address': shipping_address_qs[0]})

            billing_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='B',
                default=True
            )
            if billing_address_qs.exists():
                context.update(
                    {'default_billing_address': billing_address_qs[0]})
            return render(self.request, "checkout.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("estores:checkout")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            order_made = Order.objects.filter(user=self.request.user, ordered=True)
            
            if form.is_valid():

                use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
                if use_default_shipping:
                    print("Using the defualt shipping address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='S',
                        default=True
                    )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default shipping address available")
                        return redirect('estores:checkout')
                else:
                    print("User is entering a new shipping address")
                    shipping_address1 = form.cleaned_data.get(
                        'shipping_address')
                    shipping_address2 = form.cleaned_data.get(
                        'shipping_address2')
                    shipping_country = form.cleaned_data.get(
                        'shipping_country')
                    shipping_zip = form.cleaned_data.get('shipping_zip')

                    if is_valid_form([shipping_address1, shipping_country, shipping_zip]):
                        shipping_address = Address(
                            user=self.request.user,
                            street_address=shipping_address1,
                            apartment_address=shipping_address2,
                            country=shipping_country,
                            zip=shipping_zip,
                            address_type='S'
                        )
                        shipping_address.save()

                        order.shipping_address = shipping_address
                        order.save()

                        set_default_shipping = form.cleaned_data.get(
                            'set_default_shipping')
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()

                    else:
                        messages.info(
                            self.request, "Please fill in the required shipping address fields")

                use_default_billing = form.cleaned_data.get(
                    'use_default_billing')
                same_billing_address = form.cleaned_data.get(
                    'same_billing_address')

                if same_billing_address:
                    billing_address = shipping_address
                    billing_address.pk = None
                    billing_address.save()
                    billing_address.address_type = 'B'
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()

                elif use_default_billing:
                    print("Using the defualt billing address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='B',
                        default=True
                    )
                    if address_qs.exists():
                        billing_address = address_qs[0]
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default billing address available")
                        return redirect('estores:checkout')
                else:
                    print("User is entering a new billing address")
                    billing_address1 = form.cleaned_data.get(
                        'billing_address')
                    billing_address2 = form.cleaned_data.get(
                        'billing_address2')
                    billing_country = form.cleaned_data.get(
                        'billing_country')
                    billing_zip = form.cleaned_data.get('billing_zip')

                    if is_valid_form([billing_address1, billing_country, billing_zip]):
                        billing_address = Address(
                            user=self.request.user,
                            street_address=billing_address1,
                            apartment_address=billing_address2,
                            country=billing_country,
                            zip=billing_zip,
                            address_type='B'
                        )
                        billing_address.save()

                        order.billing_address = billing_address
                        order.save()

                        set_default_billing = form.cleaned_data.get(
                            'set_default_billing')
                        if set_default_billing:
                            billing_address.default = True
                            billing_address.save()

                    else:
                        messages.info(
                            self.request, "Please fill in the required billing address fields")
                 
                shipping_option = form.cleaned_data.get('shipping_option')
                if shipping_option == 'S':
                    order.options = 'Standard'
                    order.save()
                elif shipping_option ==  'E':
                    order.options = 'Express'
                    order.save()

                payment_option = form.cleaned_data.get('payment_option')
               

                if payment_option == 'S':
                    
                    total = 0
                    if order_made.exists():
                        for orders in order_made:
                            total += orders.get_total_add_shipping() 
                            add_order = order.get_total_add_shipping() + total
                        try:
                            budget = Budgets.objects.get(user=self.request.user)
                            if (add_order >= budget.amount):
                                return redirect('estores:budget-pass')
                        except Budgets.DoesNotExist:
                            return redirect('estores:payment', payment_option='stripe')
                    else:
                        order_price = order.get_total_add_shipping()
                        try:
                            budget = Budgets.objects.get(user=self.request.user)
                            if (order_price >= budget.amount):
                                return redirect('estores:budget-pass')
                        except Budgets.DoesNotExist:
                            return redirect('estores:payment', payment_option='stripe')
                    return redirect('estores:payment', payment_option='stripe')
                elif payment_option == 'P':
                    return redirect('estores:payment', payment_option='paypal')
                else:
                    messages.warning(
                        self.request, "Invalid payment option selected")
                    return redirect('estores:checkout')
        except ObjectDoesNotExist:
            print( "Error is here")
            messages.warning(self.request, "You do not have an active order")
            return redirect("estores:order-summary")
        
@login_required(login_url='estores:login')
def customerBudget(request):
    budget = Budgets.objects.get(user=request.user)
    order = Order.objects.get(user=request.user, ordered=False)
    order_made = Order.objects.filter(user=request.user, ordered=True)
    total = 0
    for orders in order_made:
        total += orders.get_total_add_shipping()
    new_order = order.get_total_add_shipping
    budget_balance = budget.amount - total
    total = total
    context = {
        'budget': budget,
        'total': total,
        'new_order': new_order,
        'budget_balance': budget_balance

    }
    return render(request, 'budget-pass.html', context)

class PaymentView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.billing_address:
            context = {
                'order': order,
                'DISPLAY_COUPON_FORM': False,
                'STRIPE_PUBLIC_KEY' : settings.STRIPE_PUBLIC_KEY
            }
            userprofile = self.request.user.userprofile
            if userprofile.one_click_purchasing:
                # fetch the users card list
                cards = stripe.Customer.list_sources(
                    userprofile.stripe_customer_id,
                    limit=3,
                    object='card'
                )
                card_list = cards['data']
                if len(card_list) > 0:
                    # update the context with the default card
                    context.update({
                        'card': card_list[0]
                    })
            return render(self.request, "payment.html", context)
        else:
            messages.warning(
                self.request, "You have not added a billing address")
            return redirect("estores:checkout")

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        form = PaymentForm(self.request.POST)
        userprofile = UserProfile.objects.get(user=self.request.user)
        if form.is_valid():
            token = form.cleaned_data.get('stripeToken')
            save = form.cleaned_data.get('save')
            use_default = form.cleaned_data.get('use_default')

            if save:
                if userprofile.stripe_customer_id != '' and userprofile.stripe_customer_id is not None:
                    customer = stripe.Customer.retrieve(
                                                userprofile.stripe_customer_id)
                    customer.sources.create(source=token)

                else:
                    customer = stripe.Customer.create(email=self.request.user.email,)
                    customer.sources.create(source=token)
                    userprofile.stripe_customer_id = customer['id']
                    userprofile.one_click_purchasing = True
                    userprofile.save()

            amount = int(order.get_total_add_shipping() * 100)

            try:

                if use_default or save:
                    # charge the customer because we cannot charge the token more than once
                    charge = stripe.Charge.create(
                                    amount=amount,  # cents
                                    currency="usd",
                                    customer=userprofile.stripe_customer_id
                    )
                else:
                    # charge once off on the token
                    charge = stripe.Charge.create(
                                    amount=amount,  # cents
                                    currency="usd",
                                    source=token
                    )

                # create the payment
                payment = Payment()
                payment.stripe_charge_id = charge['id']
                payment.user = self.request.user
                payment.amount = order.get_total_add_shipping()
                payment.save()

                # assign the payment to the order

                order_items = order.items.all()
                order_items.update(ordered=True)
                for item in order_items:
                                item.save()

                order.ordered = True
                order.payment = payment
                order.ref_code = create_ref_code()
                order.save()

                messages.success(self.request, "Your order was successful!")
                return redirect("/")

            except stripe.error.CardError as e:
                    body = e.json_body
                    err = body.get('error', {})
                    messages.warning(self.request, f"{err.get('message')}")
                    return redirect("/")

            except stripe.error.RateLimitError as e:
                    # Too many requests made to the API too quickly
                    messages.warning(self.request, "Rate limit error")
                    return redirect("/")

            except stripe.error.InvalidRequestError as e:
                    # Invalid parameters were supplied to Stripe's API
                    print(e)
                    messages.warning(self.request, "Invalid parameters")
                    return redirect("/")

            except stripe.error.AuthenticationError as e:
                    # Authentication with Stripe's API failed
                    # (maybe you changed API keys recently)
                    messages.warning(self.request, "Not authenticated")
                    return redirect("estores:payment", payment_option='stripe')

            except stripe.error.APIConnectionError as e:
                    # Network communication with Stripe failed
                    messages.warning(self.request, "Network error")
                    return redirect("/")

            except stripe.error.StripeError as e:
                    # Display a very generic error to the user, and maybe send
                    # yourself an email
                    messages.warning(
                                    self.request, "Something went wrong. You were not charged. Please try again.")
                    return redirect("/")

            except Exception as e:
                # send an email to ourselves
                messages.warning(
                                self.request, "A serious error occurred. We have been notifed.")
                return redirect("/")

        messages.warning(self.request, "Invalid data received")
        return redirect("/payment/stripe/")
                                
@login_required(login_url='estores:login')
def add_to_cart(request, slug):
                item = get_object_or_404(Item, slug=slug)
                order_item, created = OrderItem.objects.get_or_create(
                                item=item,
                                user=request.user,
                                ordered=False
                                )
                order_qs = Order.objects.filter(user=request.user,  ordered=False)
                if order_qs.exists():
                                order = order_qs[0]
                                # check if the order item is in the order
                                if order.items.filter(item__slug=item.slug).exists():
                                                order_item.quantity += 1
                                                order_item.save()
                                                messages.info(request, "This item quantity was updated.")
                                else:
                                                order.items.add(order_item)
                                                messages.info(request, "This item was added to your cart.")
                                                return redirect("estores:order-summary")
                else:
                                ordered_date = timezone.now()
                                order = Order.objects.create(user=request.user, ordered_date=ordered_date)
                                order.items.add(order_item)
                                messages.info(request, "This item was added to your cart.")
                return redirect("estores:order-summary")

@login_required(login_url='estores:login')
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user,  ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                            item=item,
                            user=request.user,
                            ordered=False
                            )[0]
            if order_item.quantity > 1:
                order_item.quantity = 1
                order_item.save()
            order.items.remove(order_item)
            messages.info(request, "This item was removed from your cart.")
            return redirect("estores:order-summary")
        else:
            order.items.remove(order_item)
            messages.info(request, "This item was not in your cart.")
            return redirect("estores:order-summary")
    else:
        messages.info(request, "You do not have an active order.")
        return redirect("estores:order-summary")

@login_required(login_url='estores:login')
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user,  ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                            item=item,
                            user=request.user,
                            ordered=False
                            )[0]
            if order_item.quantity > 1:
                order_item.quantity -=1
                order_item.save()
                messages.info(request, "This item quantity was updated.")
            else:
                order.items.remove(order_item)
                messages.info(request, "This item was removed from cart")
            return redirect("estores:order-summary")

        else:
            messages.info(request, "This item was not in your cart.")
            return redirect("estores:home")
    else:
        messages.info(request, "You do not have an active order.")
        return redirect("estores:home")

@login_required(login_url='estores:login')
def add_single_item_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user,  ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                        item=item,
                        user=request.user,
                        ordered=False
                        )[0]
            order_item.quantity +=1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("estores:order-summary")
        else:
            messages.info(request, "This item was not in your cart.")
            return redirect("estores:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order.")
        return redirect("estores:product", slug=slug)

def signup(request):
    if request.user.is_authenticated:
        return redirect('estores:home')
    else:
        form = SignUpForm()
        if request.method == 'POST':
            form = SignUpForm(request.POST)
            if form.is_valid():
                form.save()
                                                                
                first_name = form.cleaned_data.get("first_name")
                last_name = form.cleaned_data.get("last_name")
                phone = form.cleaned_data.get("phone")
                username = form.cleaned_data.get("username")
                email = form.cleaned_data.get("email")
                password1 = form.cleaned_data.get("password1")
                password2 = form.cleaned_data.get("password2")
                new_user = authenticate(first_name=first_name, last_name=last_name, phonenumber=phone, username=username, email=email, password=password1, password2 = password2)
                if new_user is not None:
                    login(request, new_user)
                    messages.success(request,   'Account created for '+ username )
                return redirect('estores:home')
                                
        context = {
                    'form': form
                        }
    return render(request, 'signup.html', context)

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('estores:home')
    else:
        if request.method == 'POST' and 'login' in request.POST:
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.info(request, 'You can set up a weekly or month budget to manage your spending!')
                return redirect('estores:home')
            else:
                messages.info(request, 'Username OR password is incorrect')
    context = {}
    return render(request, 'login.html', context)

def logoutUser(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('estores:login')
    else:
        return redirect('estores:login')

@login_required(login_url='estores:login')            
def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This coupon does not exist")
        return redirect("estores:order-summary")

class AddCouponView(LoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                                user=self.request.user, ordered=False)
                coupon = Coupon.objects.filter(code__iexact=code, 
                                               valid_from__lte=timezone.now(), 
                                               valid_to__gte=timezone.now()).exclude(max_value__lte=F('used')).first()
                
                if not coupon:
                    messages.error(self.request, 'You can\'t use same coupon again, or coupon does not exist')
                    return redirect('estores:order-summary')
                else:
                    if order.coupon == coupon:
                        messages.warning(self.request, "This coupon has previously been used by you.")
                        return redirect("estores:order-summary") 
                    elif order.coupon:
                        messages.warning(self.request, "You can only use a coupon for an order.")
                        return redirect("estores:order-summary") 
                    else:
                        try:
                            coupon.used += 1
                            coupon.save()
                            order.coupon = get_coupon(self.request, code)
                            order.user = self.request.user
                            order.save()
                            messages.success(self.request, "Successfully added coupon")
                            return redirect("estores:order-summary")
                        except ObjectDoesNotExist:
                            messages.info(self.request, "You do not have an active order")
                            return redirect("estores:order-summary")
            
class Shipping_Option(LoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        form = Shipping(self.request.POST)
        if form.is_valid():
            shipping_option  = form.cleaned_data.get('shipping_option')
            order = Order.objects.get(user=self.request.user, ordered=False)
            order.options = shipping_option
            order.save()

class RequestRefundView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
                    form = RefundForm()
                    context = {
                                    'form': form
                    }
                    return render(self.request, "request_refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.info(self.request, "Your request was received.")
                return redirect("estores:request-refund")

            except ObjectDoesNotExist:
                messages.info(self.request, "This order does not exist.")
                return redirect("estores:request-refund")

def get_filtered_products(request):
    min_price = request.GET.get(min_price)

    products_range = Item.objects.filter(price__gte=min_price)
    context = {
            'products_range': products_range
    }
    html = render(request, 'product_price_Range.html', context).content.decode('utf-8')
    return JsonResponse(html, safe=False)

@login_required(login_url='estores:login')
def wishList(request):
    wished_item = Wishlist.objects.filter(user=request.user)
    context ={
        'wished_item': wished_item
    }
    return render(request,  "wishlist.html", context)

@login_required(login_url='estores:login')
def add_to_wishlist(request, slug):
    item = get_object_or_404(Item, slug=slug)
    wished_item,created = Wishlist.objects.get_or_create(wished_item=item, slug=item.slug, user=request.user)
    messages.info(request, "This item was added to wishlist.")
    return redirect("estores:wishlist")

@login_required(login_url='estores:login')
def remove_from_wishlist(request, slug):
    #item = get_object_or_404(Item, slug=slug)
    wished_item = Wishlist.objects.filter(user=request.user, slug=slug)
    wished_item.delete()
    return redirect("estores:wishlist")

@login_required(login_url='estores:login')
def save_review(request, slug):
    product = Item.objects.get(slug=slug)
    user = request.user
    review = ProductReview.objects.create(
        user=user,
        product=product,
        review_text=request.POST['review_text'],
        review_rating=request.POST['review_rating']
    )
    data ={
        'user':user.username,
        'review_text':request.POST['review_text'],
        'review_rating':request.POST['review_rating']
    }

    #Fetch avg rating
    avg_reviews = ProductReview.objects.filter(product=product).aggregate(avg_rating=Avg('review_rating'))
    #End
    
    return JsonResponse({'bool': True, 'data': data, 'avg_reviews':avg_reviews, })
 
