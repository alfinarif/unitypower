from django.contrib import admin

from finance.models import PaymentRequestModel, PropertiesBuySale

from import_export import resources
from import_export.admin import ExportActionMixin
from import_export.fields import Field

class PaymentRequestModelResource(resources.ModelResource):
    user = Field()
    class Meta:
        model = PaymentRequestModel
        fields = [
            'user',
            'properties',
            'invoice_number',
            'calculation_type',
            'payment_method',
            'amount_of_money',
            'from_number',
            'pin_ref',
            'pay_month',
            'cashier',
            'payment_note',
            'is_accept',
            'status',
            'approved_by',
            'approved_at',
            'created',
        ]
        export_order = fields

    def dehydrate_user(self, obj):
        return str(obj.user.email)

    
        


class PaymentRequestAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('id', 'user', 'invoice_number', 'calculation_type', 'payment_method', 'amount_of_money', 'from_number', 'is_accept')
    resource_class = PaymentRequestModelResource


admin.site.register(PaymentRequestModel, PaymentRequestAdmin)
admin.site.register(PropertiesBuySale)


