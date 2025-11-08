from django.contrib import admin
from .models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("titulo", "publicado", "creado_en")
    list_filter = ("publicado", "creado_en")
    search_fields = ("titulo", "contenido")
    prepopulated_fields = {"slug": ("titulo",)}
