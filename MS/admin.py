from django.contrib import admin
from .models import *
from .models import Size, AgeGroup

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'category', 'price', 'user', 'is_thrift_display')
    list_filter = ('category',)
    search_fields = ('product_name', 'category')
    fields = ('product_name', 'description', 'category', 'price', 'quantity', 'image', 'user')

    def is_thrift_display(self, obj):
        return hasattr(obj, 'thriftproduct')

    is_thrift_display.short_description = 'Is Thrift'
    is_thrift_display.boolean = True


@admin.register(BiddingProduct)
class BiddingProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'starting_price', 'start_time', 'end_time')
    list_filter = ('start_time', 'end_time')
    search_fields = ('product_name', 'description')


admin.site.register(CustomUser)
admin.site.register(Bid)
admin.site.register(Order)
admin.site.register(Rating)
admin.site.register(Chat)
admin.site.register(Coupon)
admin.site.register(ThriftProduct)

admin.site.register(Size)
admin.site.register(AgeGroup)
