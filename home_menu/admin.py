from django.contrib import admin

from .models import Product, Subscription, Category, Dish, Customer, Allergy, PromotionalCode


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


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    pass


@admin.register(Allergy)
class AllergyAdmin(admin.ModelAdmin):
    pass


@admin.register(PromotionalCode)
class PromotionalCodeAdmin(admin.ModelAdmin):
    pass
