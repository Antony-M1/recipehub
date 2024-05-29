from django.contrib import admin
from .models import (
    User,
    Recipe,
    Category,
    Review
)
# Register your models here.

admin.AdminSite.site_header = 'Recipe Hub Admin'


class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'phone_number', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('email', 'is_active', 'is_staff')
    ordering = ('-date_joined',)
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    prepopulated_fields = {'email': ('email',), 'phone_number': ('phone_number',)}


admin.site.register(User, UserAdmin)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'user_id', 'category', 'cooking_time', 'serving_size', 'created_at', 'updated_at')
    list_filter = ('title', 'user_id', 'category', 'cooking_time', 'serving_size')
    ordering = ('-created_at',)
    search_fields = ('title', 'user', 'category', 'cooking_time', 'serving_size')
    prepopulated_fields = {'title': ('title',)}

admin.site.register(Recipe, RecipeAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    list_filter = ('name', 'description')
    ordering = ('-name',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'name': ('name',)}

admin.site.register(Category, CategoryAdmin)


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'rating', 'comment', 'created_at')
    list_filter = ('user', 'recipe', 'rating', 'comment')
    ordering = ('-created_at',)
    search_fields = ('user', 'recipe', 'rating', 'comment')


admin.site.register(Review, ReviewAdmin)