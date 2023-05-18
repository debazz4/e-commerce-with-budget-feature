from dataclasses import field
from pyexpat import model
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.urls import clear_script_prefix
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

class SignUpForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({
            'type':"text",
            'class':"form-control",
            'id':"username",
            'name':"username",
            'required':'',
		})
        self.fields["email"].widget.attrs.update({
            'type':"email",
            'class':"form-control",
            'id':"register-email-1",
            'name':"register-email",
            'required':'',
		})
        self.fields["password1"].widget.attrs.update({
            'type':"password", 
            'class':"form-control", 
            'id':"register-password-1",
            'name':"register-password",
            'required':"",					    		
        })
        self.fields["password2"].widget.attrs.update({
            'type':"password", 
            'class':"form-control", 
            'id':"register-password-2",
            'name':"register-password",
            'required':"",					    		
        })

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'PayPal')
)

SHIPPING_CHOICES = (
    ('S', 'Standard'),
    ('E', 'Express'),
)

class Shipping(forms.Form):
    shipping_option = forms.ChoiceField(widget=forms.RadioSelect, choices=SHIPPING_CHOICES)
    cost = forms.CharField(required=False)

class CheckoutForm(forms.Form):
    shipping_address = forms.CharField(required=False)
    shipping_address2 = forms.CharField(required=False)
    shipping_country = CountryField(blank_label='(select country)').formfield(
        required=False,
        widget=CountrySelectWidget(attrs={
            'class': 'form-control',
        }))
    shipping_state = forms.CharField(required=False)
    shipping_zip = forms.CharField(required=False)

    billing_address = forms.CharField(required=False)
    billing_address2 = forms.CharField(required=False)
    billing_country = CountryField(blank_label='(select country)').formfield(
        required=False,
        widget=CountrySelectWidget(attrs={
            'class': 'form-control',
        }))
    billing_state = forms.CharField(required=False)
    billing_zip = forms.CharField(required=False)

    same_billing_address = forms.BooleanField(required=False)
    set_default_shipping = forms.BooleanField(required=False)
    use_default_shipping = forms.BooleanField(required=False)
    set_default_billing = forms.BooleanField(required=False)
    use_default_billing = forms.BooleanField(required=False)

    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_CHOICES)
    



class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Promo code',
        'aria-label': 'Recipient\'s username',
        'aria-describedby': 'basic-addon2'
    }))


class RefundForm(forms.Form):
    ref_code = forms.CharField()
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 4
    }))
    email = forms.EmailField()


class PaymentForm(forms.Form):
    stripeToken = forms.CharField(required=False)
    save = forms.BooleanField(required=False)
    use_default = forms.BooleanField(required=False)

    
