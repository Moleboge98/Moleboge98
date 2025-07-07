from django import forms
from .models import User, Store, Product, Review, Category

# =================
# STYLING WIDGETS
# To avoid repeating the same CSS classes, we can define them here.
# =================

# Standard classes for text-based inputs and select dropdowns
form_field_classes = 'mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'

# Classes for file inputs
file_input_classes = 'mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'


# =================
# USER & AUTH FORMS
# =================

class UserRegistrationForm(forms.ModelForm):
    """Form for users to sign up."""
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': form_field_classes})
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'user_type']
        widgets = {
            'username': forms.TextInput(attrs={'class': form_field_classes}),
            'email': forms.EmailInput(attrs={'class': form_field_classes}),
            'user_type': forms.Select(attrs={'class': form_field_classes}),
        }

    def save(self, commit=True):
        # Override the save method to handle password hashing.
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class UserLoginForm(forms.Form):
    """Form for users to log in."""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': form_field_classes, 'placeholder': 'you@example.com'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': form_field_classes, 'placeholder': 'Your Password'})
    )


# =================
# VENDOR & PRODUCT FORMS
# =================

class StoreForm(forms.ModelForm):
    """Form for vendors to create or edit their store."""
    class Meta:
        model = Store
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': form_field_classes}),
            'description': forms.Textarea(attrs={'class': form_field_classes, 'rows': 4}),
        }

class ProductForm(forms.ModelForm):
    """Form for vendors to add or edit products."""
    # The category field will be a dropdown of existing categories.
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=forms.Select(attrs={'class': form_field_classes})
    )

    class Meta:
        model = Product
        # ADDED 'category' to the list of fields.
        fields = ['name', 'category', 'description', 'price', 'stock', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': form_field_classes}),
            'description': forms.Textarea(attrs={'class': form_field_classes, 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': form_field_classes}),
            'stock': forms.NumberInput(attrs={'class': form_field_classes}),
            'image': forms.ClearableFileInput(attrs={'class': file_input_classes}),
        }


# =================
# REVIEW FORM
# =================

class ReviewForm(forms.ModelForm):
    """Form for buyers to leave a review on a product."""
    RATING_CHOICES = [(5, '5 Stars'), (4, '4 Stars'), (3, '3 Stars'), (2, '2 Stars'), (1, '1 Star')]
    
    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.Select(attrs={'class': form_field_classes})
    )
    
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'class': form_field_classes, 
                'rows': 4, 
                'placeholder': 'Write your review here...'
            }),
        }
