from django.contrib import admin
from .models import Document

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'level', 'semester', 'upload_date')
    list_filter = ('category', 'level', 'semester')
    search_fields = ('title', 'description')
    date_hierarchy = 'upload_date'
    ordering = ('-upload_date',)
