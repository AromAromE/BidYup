from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

#ต้องมาเพิ่มเพราะทำการใช้ custom user เลยต้องเพิ่มให้ user กลับมาหน้า admin
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
