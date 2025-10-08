from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Item, Bid
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from decimal import Decimal

User = get_user_model()

ROLE_CHOICES = (
    ('buyer', 'Buyer'),
    ('seller', 'Seller'),
)

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Password'
        })
    )

class RegisterForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Username'
        })
    )
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Last Name'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Email'
        })
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Password'
        })
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Confirm Password'
        })
    )
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-green-500 appearance-none',
        })
    )
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'เบอร์โทรศัพท์ (ไม่บังคับ)'
        })
    )
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'ที่อยู่ (ไม่บังคับ)',
            'rows': 3
        })
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'phone', 'address']

class CreateForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['title', 'description', 'starting_price', 'image', 'end_time', 'category']

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500',
                'placeholder': 'ชื่อสินค้า'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500',
                'rows': 4,
                'placeholder': 'รายละเอียดสินค้า'
            }),
            'starting_price': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500',
                'placeholder': 'ราคาเริ่มต้น'
            }),
            'image': forms.ClearableFileInput(attrs={
                # 'class': 'hidden'
            }),
            'end_time': forms.DateTimeInput(attrs={
                'class': 'w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500',
                'type': 'datetime-local',
                'min': timezone.now().strftime('%Y-%m-%dT%H:%M')
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-green-500 appearance-none',
            }),
        }
    
    def clean_end_time(self):
        end_time = self.cleaned_data.get("end_time")
        if end_time and end_time <= timezone.now():
            raise forms.ValidationError("⏰ เวลาสิ้นสุดต้องอยู่ในอนาคตเท่านั้น")
        return end_time

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ["amount"]

    def __init__(self, *args, **kwargs):
        self.current_price = kwargs.pop("current_price", Decimal("0"))
        super().__init__(*args, **kwargs)
        self.fields["amount"].widget.attrs.update({
            "class": "w-full p-2 rounded-md bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500",
            "placeholder": "ใส่ราคาที่คุณต้องการเสนอ",
        })

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount <= self.current_price:
            raise forms.ValidationError(
                f"❌ ราคาต้องสูงกว่าราคาปัจจุบัน ({self.current_price})"
            )
        return amount


class ProfileForm(forms.ModelForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Username'
        })
    )
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Last Name'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Email'
        })
    )
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'เบอร์โทรศัพท์ (ไม่บังคับ)'
        })
    )
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'ที่อยู่ (ไม่บังคับ)',
            'rows': 3
        })
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'รหัสผ่าน'
        })
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'ยืนยันรหัสผ่าน'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'address']

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 or password2:
            if password1 != password2:
                raise forms.ValidationError("รหัสผ่านทั้งสองช่องไม่ตรงกัน")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password1")
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user
