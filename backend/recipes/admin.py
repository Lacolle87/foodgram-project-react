from django import forms
from django.contrib import admin

from .models import (
    Tag,
    Recipe,
    Ingredient,
    RecipeIngredient,
    Favorite,
    ShoppingCart
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    list_filter = ('recipes',)
    prepopulated_fields = {'slug': ('name',)}


class IngredientsFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()

        if any(self.errors):
            return

        ingredient_count = 0
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE',
                                                               False):
                ingredient_count += 1
            if ingredient_count < 1:
                raise forms.ValidationError(
                    'Добавьте хотя бы один ингредиент'
                )


class IngredientRecipeInline(admin.TabularInline):
    model = RecipeIngredient
    formset = IngredientsFormSet


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_filter = ('author', 'tags')
    list_display = ('name', 'author', 'is_favorited',
                    'pub_date')
    search_fields = ('author', 'name', 'tags')
    inlines = [IngredientRecipeInline]

    def is_favorited(self, obj):
        return obj.favorite.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('measurement_unit',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')
