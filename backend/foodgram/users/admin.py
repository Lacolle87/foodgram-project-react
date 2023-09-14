from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import AuthorSubscription, User


@admin.register(User)
class CustomUserAmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('username', 'email')


@admin.register(AuthorSubscription)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
