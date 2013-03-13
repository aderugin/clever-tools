from django.contrib import admin
from .models import *


class OrderItemInline(admin.StackedInline):
    model = OrderItem
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'status',
        'user_name',
        'delivery_date',
        'delivery_time',
        'location',
        'adress',
        'user_phone',
        'total_cost_with_sale',
        'comment',
        'created_at',
        'updated_at',
    )
    search_fields = ('adress', 'user_name', 'id', 'code')
    inlines = [OrderItemInline]


class LocationDeliveryCostInline(admin.StackedInline):
    model = LocationDeliveryCost
    extra = 1

# class PaymentInline(admin.StackedInline):
#     model = Payment
#     extra = 1


class DeliveryAdmin(admin.ModelAdmin):
    inlines = [LocationDeliveryCostInline]


class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ('status', 'message', )
    search_fields = ('status', 'message', )
    filter_fields = ('status', )

admin.site.register(StoreSettings)
admin.site.register(OrderDiscount)
admin.site.register(Order, OrderAdmin)
admin.site.register(Delivery, DeliveryAdmin)
admin.site.register(Payment)
admin.site.register(DeliveryLocation)
admin.site.register(OrderStatus, OrderStatusAdmin)
