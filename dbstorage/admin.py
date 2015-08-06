from django.contrib import admin
from .models import StoredFile

class StoredFileAdmin(admin.ModelAdmin):
	list_display = ['path', 'mime_type', 'size', 'created', 'updated']
	search_fields = ['path']

admin.site.register(StoredFile, StoredFileAdmin)
