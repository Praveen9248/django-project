from django.contrib import admin
from .models import Group,Expense,Payment

admin.site.register(Group)
admin.site.register(Expense)
admin.site.register(Payment)