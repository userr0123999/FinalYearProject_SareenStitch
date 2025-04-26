from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from .models import (
    Product, ThriftProduct, BiddingProduct, Rating,
    Chat, Vendor, Profile, Size, AgeGroup
)

User = get_user_model()


# ✅ User Registration Form
class CustomUserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter Password'}), label='Password')
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}), label='Confirm Password')

    class Meta:
        model = User
        fields = ['first_name', 'username', 'email', 'password']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Enter Full Name'}),
            'username': forms.TextInput(attrs={'placeholder': 'Enter Username'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter Email'}),
        }
        labels = {
            'first_name': 'Full Name',
        }

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password") != cleaned_data.get("confirm_password"):
            raise ValidationError("Passwords do not match.")
        return cleaned_data


# ✅ Login Form
class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username', 'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-control'}))

from django import forms
from .models import Product, Size

class ProductForm(forms.ModelForm):
    size = forms.ModelMultipleChoiceField(
        queryset=Size.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label='Sizes (select multiple)'
    )

    class Meta:
        model = Product
        fields = [
            'product_name', 'description', 'category', 'price',
            'quantity', 'size', 'image'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }



# ✅ Vendor Product Form (inherits from ProductForm)
class VendorProductForm(ProductForm):
    age_group = forms.ChoiceField(
        choices=[
            ('8-10', '8–10 Years'),
            ('11-14', '11–14 Years'),
            ('15-17', '15–17 Years'),
            ('18-19', '18–19 Years'),
            ('20-24', '20–24 Years'),
            ('25-29', '25–29 Years'),
            ('30-34', '30–34 Years'),
            ('35-39', '35–39 Years'),
        ],
        required=True,
        label='Age Group'
    )

    class Meta(ProductForm.Meta):
        fields = ProductForm.Meta.fields + ['age_group']




# ✅ Thrift Product Form
class ThriftProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'description', 'category', 'price', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


# ✅ Thrift Extra Fields
class ThriftExtraForm(forms.ModelForm):
    CONDITION_CHOICES = [(str(i), f"{i} - Excellent" if i == 5 else str(i)) for i in range(1, 6)]

    condition_rating = forms.ChoiceField(
        choices=CONDITION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = ThriftProduct
        fields = ['condition_rating']


# Bidding Product Form
from django import forms
from .models import BiddingProduct

class BiddingProductForm(forms.ModelForm):
    class Meta:
        model = BiddingProduct
        fields = ['product_name', 'description', 'image', 'starting_price', 'estimated_price', 'start_time', 'end_time']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }



# ✅ Chat Form
class ChatForm(forms.ModelForm):
    class Meta:
        model = Chat
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Type your message...'}),
        }


# ✅ Rating Form
class ThriftRatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating', 'review']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'review': forms.Textarea(attrs={'rows': 3}),
        }


# ✅ Profile Image Form
class ProfileImageForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_image']
