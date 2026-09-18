from django.contrib import admin

from finance.models import (
    PaymentModel, 
    Properties,
    FeeSchedule, 
    PaymentType,
    PaymentMethod,
    Cashier,
    DuePayment,
    PaymentSummery
)

from import_export import resources
from import_export.admin import ExportActionMixin
from import_export.fields import Field

class PaymentRequestModelResource(resources.ModelResource):
    user = Field()
    class Meta:
        model = PaymentModel
        fields = [
            'user',
            'properties',
            'invoice_number',
            'payment_type',
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
    list_display = ('id', 'user', 'invoice_number', 'payment_type', 'payment_method', 'amount_of_money', 'from_number', 'is_accept')
    resource_class = PaymentRequestModelResource


class DuePaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'due_amount', 'pay_year', 'pay_month', 'penalty_fee', 'is_penalty', 'status', 'created')



class PaymentSummeryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_due_amount', 'total_penalty_amount', 'total_paid_amount', 'is_active', 'created')




class PropertiesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'status', 'approved_by', 'created_at')

admin.site.register(PaymentType)
admin.site.register(PaymentMethod)
admin.site.register(Cashier)
admin.site.register(FeeSchedule)
admin.site.register(Properties, PropertiesAdmin)
admin.site.register(PaymentModel, PaymentRequestAdmin)
admin.site.register(DuePayment, DuePaymentAdmin)
admin.site.register(PaymentSummery, PaymentSummeryAdmin)
