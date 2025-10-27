from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user



from django import forms
from .models import Farm

class FarmForm(forms.ModelForm):
    class Meta:
        model = Farm
        exclude = ['owner']
        fields = ['name', 'address', 'city', 'size']


from shops.models import Shop, RequestedShop

class RequestedShopForm(forms.ModelForm):
    class Meta:
        model = RequestedShop
        fields = ["name", "address", "city", "contact_number"]