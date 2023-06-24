from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username',  'password', 'email', 'first_name',
                    'last_name', 'role',)
    list_display_links = ('username',)
    list_editable = ('role',)
    list_filter = ('role',)
    search_fields = ('username', 'email',)
