from django.contrib import admin
from .models import Users, DeliveryPartner, Address, Products, EachItem, Cart, PaymentDetails, Orders

class AdminUsers(admin.ModelAdmin):
    list_display= [
        "username",
        'name',
        'phone',
        'email',
        'address',
    ]
admin.site.register(Users,AdminUsers)

class AdminDP(admin.ModelAdmin): 
    list_display=[
        'name',
        'phone',
        'location',
    ]
admin.site.register(DeliveryPartner,AdminDP)

class AdminAdres(admin.ModelAdmin):
    list_display=[
        'user',
        'country',
        'state',
        'city',
        'postal_code',
    ]
admin.site.register(Address,AdminAdres)

class AdminProduct(admin.ModelAdmin):
    list_display=[
        'product_id',
        'name',
        'sellingPrice',
        'stock',
        'discount',
    ]
admin.site.register(Products,AdminProduct)

class AdminEI(admin.ModelAdmin):
    list_display=[
        'user',
        'product',
        'quantity',
    ]
admin.site.register(EachItem,AdminEI)

class AdminCart(admin.ModelAdmin):
    list_display=[
        'user',
        'total',
    ]
admin.site.register(Cart,AdminCart)

class AdminPayDetail(admin.ModelAdmin):
    list_display=[
        'user',
        'card_number',
        'billing_address',
        'zip_code',
    ]
admin.site.register(PaymentDetails,AdminPayDetail)

class AdminOrders(admin.ModelAdmin):
    list_display=[
        'order_id',
        'user',
        'delivery_partner',
        'status',
        'payment_method',
        'expected_delivery',
    ]
admin.site.register(Orders,AdminOrders) 