from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm
from .models import Item, Bid
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal

User = get_user_model()

ROLE_CHOICES = (
    ("buyer", "Buyer"),
    ("seller", "Seller"),
)

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="ชื่อผู้ใช้",
        widget=forms.TextInput(attrs={
            "class": "w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent",
            "placeholder": "ชื่อผู้ใช้"   
        })
    )
    password = forms.CharField(
        label="รหัสผ่าน",
        widget=forms.PasswordInput(attrs={
            "class": "w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent",
            "placeholder": "รหัสผ่าน"
        })
    )

class RegisterForm(UserCreationForm):
    username = forms.CharField(
        label="ชื่อผู้ใช้",
        widget=forms.TextInput(attrs={
            "class": "w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent",
            "placeholder": "ชื่อผู้ใช้"
        })
    )
    first_name = forms.CharField(
        label="ชื่อจริง",
        required=True,
        widget=forms.TextInput(attrs={
            "class": "w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent",
            "placeholder": "ชื่อจริง"
        })
    )
    last_name = forms.CharField(
        label="นามสกุล",
        required=True,
        widget=forms.TextInput(attrs={
            "class": "w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent",
            "placeholder": "นามสกุล"
        })
    )
    email = forms.EmailField(
        label="อีเมล",
        required=True,
        widget=forms.EmailInput(attrs={
            "class": "w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent",
            "placeholder": "อีเมล"
        })
    )
    password1 = forms.CharField(
        label="รหัสผ่าน",
        widget=forms.PasswordInput(attrs={
            "class": "w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent",
            "placeholder": "รหัสผ่าน"
        })
    )
    password2 = forms.CharField(
        label="ยืนยันรหัสผ่าน",
        widget=forms.PasswordInput(attrs={
            "class": "w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent",
            "placeholder": "ยืนยันรหัสผ่าน"
        })
    )
    role = forms.ChoiceField(
        label="บทบาท",
        choices=ROLE_CHOICES,
        widget=forms.Select(attrs={
            "class": "w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-green-500 appearance-none",
        })
    )
    phone = forms.CharField(
        label="เบอร์โทรศัพท์",
        required=False,
        widget=forms.TextInput(attrs={
            "class": "w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent",
            "placeholder": "เบอร์โทรศัพท์ (ไม่บังคับ)"
        })
    )
    address = forms.CharField(
        label="ที่อยู่",
        required=False,
        widget=forms.Textarea(attrs={
            "class": "w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent",
            "placeholder": "ที่อยู่ (ไม่บังคับ)",
            "rows": 3
        })
    )

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email","password1", "password2"]

class CreateForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ["title", "description", "starting_price", "image", "end_time", "category"]

        labels = {
            "title": "ชื่อสินค้า",
            "description": "รายละเอียดสินค้า",
            "starting_price": "ราคาเริ่มต้น",
            "image": "รูปภาพสินค้า",
            "end_time": "เวลาสิ้นสุดการประมูล",
            "category": "หมวดหมู่",
        }
    
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500",
                "placeholder": "ชื่อสินค้า"
            }),
            "description": forms.Textarea(attrs={
                "class": "w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500",
                "rows": 4,
                "placeholder": "รายละเอียดสินค้า"
            }),
            "starting_price": forms.NumberInput(attrs={
                "class": "w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500",
                "placeholder": "ราคาเริ่มต้น"
            }),
            "image": forms.ClearableFileInput(attrs={
                "class": "hidden",
                "id": "id_image",
                "required": "required"
            }),
            "end_time": forms.DateTimeInput(attrs={
                "class": "w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500",
                "type": "datetime-local",
                "min": timezone.now().strftime("%Y-%m-%dT%H:%M")
            }),
            "category": forms.Select(attrs={
                "class": "w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-green-500 appearance-none",
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
        label="ชื่อผู้ใช้",
        widget=forms.TextInput(attrs={
            "class": "w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent",
            "placeholder": "Username"
        })
    )
    first_name = forms.CharField(
        required=True,
        label="ชื่อจริง",
        widget=forms.TextInput(attrs={
            "class": "w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent",
            "placeholder": "First Name"
        })
    )
    last_name = forms.CharField(
        required=True,
        label="นามสกุล",
        widget=forms.TextInput(attrs={
            "class": "w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent",
            "placeholder": "Last Name"
        })
    )
    email = forms.EmailField(
        required=True,
        label="อีเมล",
        widget=forms.EmailInput(attrs={
            "class": "w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent",
            "placeholder": "Email"
        })
    )
    phone = forms.CharField(
        required=False,
        label="เบอร์โทร",
        widget=forms.TextInput(attrs={
            "class": "w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent",
            "placeholder": "เบอร์โทรศัพท์ (ไม่บังคับ)"
        })
    )
    address = forms.CharField(
        required=False,
        label="ที่อยู่",
        widget=forms.Textarea(attrs={
            "class": "w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent",
            "placeholder": "ที่อยู่ (ไม่บังคับ)",
            "rows": 3
        })
    )

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "phone", "address"]

class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="รหัสผ่านเดิม",
        widget=forms.PasswordInput(attrs={
            "class": "w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 "
                     "focus:ring-2 focus:ring-blue-500 focus:border-transparent",
            "placeholder": "รหัสผ่านเก่า"
        })
    )
    new_password1 = forms.CharField(
        label="รหัสผ่านใหม่",
        widget=forms.PasswordInput(attrs={
            "class": "w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 "
                     "focus:ring-2 focus:ring-blue-500 focus:border-transparent",
            "placeholder": "รหัสผ่านใหม่"
        })
    )
    new_password2 = forms.CharField(
        label="ยืนยันรหัสผ่านใหม่",
        widget=forms.PasswordInput(attrs={
            "class": "w-full px-3 py-2 rounded-lg bg-gray-700 text-white border border-gray-600 "
                     "focus:ring-2 focus:ring-blue-500 focus:border-transparent",
            "placeholder": "ยืนยันรหัสผ่านใหม่"
        })
    )
