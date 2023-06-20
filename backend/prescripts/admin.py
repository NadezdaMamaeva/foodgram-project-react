from django.contrib import admin

from .models import (Tag, Prescriptor,)


class TagAdmin(admin.ModelAdmin):
    list_display = ('slug', 'name', 'color',)
    list_filter = ('color',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',), }


class PrescriptorAdmin(admin.ModelAdmin):
    list_display = ('author', 'name', 'get_tags',)
    list_display_links = ('author',)
    list_editable = ('name',)
    list_filter = ('author', 'name', 'tags',)
    empty_value_display = '-'
    search_fields = ('name',)

    @admin.display(description='Теги')
    def get_tags(self, obj):
        return ','.join([tag.name for tag in obj.tags.all()])


admin.site.register(Tag, TagAdmin)
admin.site.register(Prescriptor, PrescriptorAdmin)
