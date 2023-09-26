from django.contrib import admin

from .models import Product, Subscription, Category, Dish


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'title',
    ]


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        'title',
    ]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        'title',
    ]


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = [
        'title',
    ]
