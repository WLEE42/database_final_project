from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import *


# 管理用户

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ('uemail', 'uname', 'is_staff', 'is_active',)
    list_filter = ('uemail', 'uname', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('uemail', 'uname', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
        # ('Groups', {'fields': ('groups',)}),
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


# 管理书籍

class BookcopyInline(admin.TabularInline):
    model = Bookcopy
    min_num = 1
    extra = 0
    exclude = ['bcid']


class BookAdmin(admin.ModelAdmin):
    inlines = [BookcopyInline]
    list_display = ('bname', 'bauthor', 'bpubtime')
    list_filter = ('bpubcomp',)
    search_fields = ('bname', 'bauthor')
    fieldsets = (
        ['Main', {
            'fields': ('bname', 'bauthor', 'bpubtime', 'bpubcomp',),
        }],
        ['Advance', {
            # 'classes': ('collapse',),
            'fields': ('bimage', 'bsummary'),
        }]
    )


admin.site.register(Book, BookAdmin)

# 管理房间
admin.site.register(Room)

# 管理借阅、罚款、预约
admin.site.register(Penalty)
admin.site.register(Reserve)
admin.site.register(Borrow)
