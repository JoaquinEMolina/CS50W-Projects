from django.contrib import admin
from .models import Category, Bid, Listing, Comment, User
from django.contrib.auth.admin import UserAdmin
# Register your models here.

admin.site.register(Category)
admin.site.register(Bid)
admin.site.register(Listing)
admin.site.register(Comment)
admin.site.register(User, UserAdmin)
