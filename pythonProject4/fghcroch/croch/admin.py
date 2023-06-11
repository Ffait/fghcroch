from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin

from .models import *


class ProductInline(admin.TabularInline):
    model = Products


class CartItemInline(admin.TabularInline):
    model = Cartitem


class ProductsAdmin (admin.ModelAdmin):
    list_display = ('name', 'price', 'cat')
    list_display_links = ('name',)
    search_fields = ('name', )
    list_editable = ('cat', 'price')
    list_filter = ('price', )
    prepopulated_fields = {"slug": ("name", )}


class CategoryAdmin (admin.ModelAdmin):
    list_display = ('name', )
    list_display_links = ('name', )
    search_fields = ('name', )
    prepopulated_fields = {"slug": ("name", )}


class CartItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'cart', 'price']


class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'id', ]
    inlines = [CartItemInline, ]


class OrderItemInline(admin.TabularInline):
    model = OrderItem


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'payment_method', 'delivery_method', 'status', 'created_at']
    inlines = [OrderItemInline]


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'birth_date', 'slug')
    list_display_links = ('user', 'slug')


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('email', 'user')
    list_display_links = ('email',)


class CommentAdmin(DraggableMPTTAdmin):
    list_display = ('tree_actions', 'indented_title', 'product', 'author', 'time_create', 'status')
    mptt_level_indent = 2
    list_display_links = ('product',)
    list_filter = ('time_create', 'time_update', 'author')
    list_editable = ('status',)


admin.site.register(Products, ProductsAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Cartitem, CartItemAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Order, OrderAdmin)


