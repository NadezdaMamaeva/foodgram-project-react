from django.contrib import admin

from .models import (Component, ComponentUnit, Favorite, Recipe,
                     ShoppingCart, Tag,)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('slug', 'name', 'color',)
    list_filter = ('color',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',), }


class RecipeComponentInLine(admin.TabularInline):
    model = Recipe.ingredients.through
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author', 'name', 'get_tags',)
    list_display_links = ('author',)
    list_editable = ('name',)
    list_filter = ('author', 'name', 'tags',)
    empty_value_display = '-пусто-'
    search_fields = ('name', 'cooking_time', 'ingredients__name',)
    inlines = (RecipeComponentInLine,)

    @admin.display(description='Теги')
    def get_tags(self, obj):
        return ','.join([tag.name for tag in obj.tags.all()])


@admin.register(ComponentUnit)
class ComponentUnitAdmin(admin.ModelAdmin):
    list_display = ('slug', 'name',)
    list_display_links = ('slug',)
    list_editable = ('name',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',), }


@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit',)
    list_display_links = ('unit',)
    list_editable = ('name',)
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe',)
    list_display_links = ('id',)
    list_editable = ('recipe',)
    list_filter = ('user',)
    search_fields = ('recipe',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe',)
    list_display_links = ('id',)
    list_editable = ('recipe',)
    list_filter = ('user',)
    search_fields = ('recipe',)
