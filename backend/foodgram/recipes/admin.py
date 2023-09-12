from django.contrib import admin

from recipes.models import Tag

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass
