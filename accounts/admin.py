from django.contrib import admin
from .models import MyAccountManager,Account
from django.contrib.auth.admin import UserAdmin
# Register your models here.

class AccountAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'username','date_joined','is_active')
    list_display_links = ('first_name', 'last_name', 'username')
    

    list_filter = ()
    filter_horizontal = ()
    fieldsets = ()

admin.site.register(Account, AccountAdmin)
