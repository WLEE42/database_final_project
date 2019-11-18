from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import *


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ('uemail', 'is_staff', 'is_active',)
    list_filter = ('uemail', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('uemail', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
        ('Groups', {'fields': ('groups',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('uemail', 'password1', 'password2', 'is_staff', 'is_active')}
         ),
    )
    search_fields = ('uemail',)
    ordering = ('uemail',)


admin.site.register(User, CustomUserAdmin)

admin.site.register(Borrow)

class BookAdmin(admin.ModelAdmin):
    list_display = ('bid', 'bname', 'bauthor')


admin.site.register(Book, BookAdmin)
