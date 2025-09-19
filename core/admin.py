from django.contrib import admin
from .models import Document, UE, ECUE

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'level', 'semester', 'ecue', 'upload_date')
    list_filter = ('category', 'level', 'semester', 'ecue')
    search_fields = ('title', 'description', 'ecue__name', 'ecue__ue__name')
    date_hierarchy = 'upload_date'
    ordering = ('-upload_date',)


@admin.register(UE)
class UEAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'level', 'semester')
    list_filter = ('level', 'semester')
    search_fields = ('code', 'name')
    prepopulated_fields = { 'slug': ('name',) }


@admin.register(ECUE)
class ECUEAdmin(admin.ModelAdmin):
    list_display = ('name', 'ue')
    list_filter = ('ue__level', 'ue__semester', 'ue')
    search_fields = ('name', 'ue__name', 'ue__code')
    prepopulated_fields = { 'slug': ('name',) }
