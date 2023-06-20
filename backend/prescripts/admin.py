from django.contrib import admin

from .models import (Component, ComponentUnit, Prescriptor, Tag,)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('slug', 'name', 'color',)
    list_filter = ('color',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',), }


class PrescriptorComponentInLine(admin.TabularInline):
    model = Prescriptor.components.through
    extra = 1


@admin.register(Prescriptor)
class PrescriptorAdmin(admin.ModelAdmin):
    list_display = ('author', 'name', 'get_tags',)
    list_display_links = ('author',)
    list_editable = ('name',)
    list_filter = ('author', 'name', 'tags',)
    empty_value_display = '-пусто-'
    search_fields = ('name', 'cooking_time', 'components__name',)
    inlines = (PrescriptorComponentInLine,)

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
