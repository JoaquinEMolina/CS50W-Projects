from django import forms
from .models import Listing, Category

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'initial_price', 'image_url', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Title'}),
            'description': forms.TextInput(attrs={'placeholder': 'Description'}),
            'initial_price': forms.NumberInput(attrs={'placeholder': 'Initial Price'}),
            'image_url': forms.URLInput(attrs={'placeholder': 'Image URL'}),
            'category': forms.Select()
        }