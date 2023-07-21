from dataclasses import field
from pyexpat import model
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.urls import clear_script_prefix
from django.core.validators import RegexValidator
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from .models import ProductReview

class SignUpForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].widget.attrs.update({
            'type':"text",
            'class':"form-control",
            'id':"first_name",
            'name':"first_name",
            'required':'',
		})
        self.fields["last_name"].widget.attrs.update({
            'type':"text",
            'class':"form-control",
            'id':"last_name",
            'name':"last_name",
            'required':'',
		})
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

    phone_regex = RegexValidator(regex=r'^\+?1?\d{2,13}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone = forms.CharField(validators=[phone_regex], max_length=17, widget=forms.TextInput(attrs={
            'type':"text", 
            'class':"form-control", 
            'id':"phone",
            'name':"phone",
            'required':"",					    		
        }))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone','username', 'email', 'password1', 'password2']

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

    shipping_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=SHIPPING_CHOICES)
    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_CHOICES)
    



class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Promo code',
        'aria-label': 'Recipient\'s username',
        'aria-describedby': 'basic-addon2'
    }))
    

class BudgetForm(forms.Form):
    budget_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Budget Name',
        'aria-label': 'Recipient\'s username',
        'aria-describedby': 'basic-addon2'
    }))
    amount = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Amount Target',
        'aria-label': 'Recipient\'s username',
        'aria-describedby': 'basic-addon2'
    }))
    duration = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Duration',
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

class ReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields=('review_text', 'review_rating')
    
