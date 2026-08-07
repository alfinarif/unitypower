from django.contrib import admin
from membership.models import User, Profile, Nominee, ContactUs

from import_export import resources
from import_export.admin import ExportActionMixin
from import_export.fields import Field


class UserModelResource(resources.ModelResource):
    
    class Meta:
        model = User
        fields = [
            'email',
            'account_number',
            'user_type',
            'is_hr',
            'is_admin',
            'is_finance',
            'date_joined',
        ]
        export_order = fields




# Register models here.
class UserModelAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('id', 'email', 'account_number', 'user_type', 'is_hr', 'is_admin', 'is_finance', 'date_joined')
    resource_class = UserModelResource


class ProfileModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_date')
    readonly_fields = ('created_date',)

admin.site.register(User, UserModelAdmin)
admin.site.register(Profile, ProfileModelAdmin)
admin.site.register(Nominee)
admin.site.register(ContactUs)
