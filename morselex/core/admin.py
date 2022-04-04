from django.contrib import admin

from core import models

class TaggingInline(admin.TabularInline):
    model = models.Tagging
    extra = 1

class AttributeInline(admin.TabularInline):
    model = models.Attribute
    extra = 1

class MorselAdmin(admin.ModelAdmin):
    inlines = [
        TaggingInline,
        AttributeInline,
    ]

admin.site.register(models.Morsel, MorselAdmin)


class MorselInline(admin.TabularInline):
    model = models.Morsel
    extra = 1

class WorkspaceAdmin(admin.ModelAdmin):
    inlines = [
        MorselInline,
    ]

admin.site.register(models.Workspace, WorkspaceAdmin)