from django.contrib import admin

from models import DishCategory, Dish, Restaurant


class DishCategoryMembershipInline(admin.TabularInline):
    model = DishCategory.restaurants.through


class DishAdmin(admin.TabularInline):
    model = Dish


class DishCategoryAdmin(admin.ModelAdmin):
    model = DishCategory
    inlines = [DishCategoryMembershipInline, DishAdmin,]
    exclude = ('restaurants',)


class RestaurantAdmin(admin.ModelAdmin):
    model = Restaurant
    inlines = [DishCategoryMembershipInline,]


admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(DishCategory, DishCategoryAdmin)
