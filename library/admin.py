from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(User)
admin.site.register(Borrow)


class BookAdmin(admin.ModelAdmin):
    list_display = ('bid', 'bname', 'bauthor')


admin.site.register(Book, BookAdmin)
# admin.s
