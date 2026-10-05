from django.contrib import admin
from .models import Product, Order, Contact, OldOrder, Blog

# Register your models here.
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Contact)
admin.site.register(OldOrder)
admin.site.register(Blog)