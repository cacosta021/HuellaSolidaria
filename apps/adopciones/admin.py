from django.contrib import admin
from django.utils.html import mark_safe
from .models import (
    TipoMascota, EstadoMascota, Raza,
    Mascota, MascotaImagen, PostulacionAdopcion, RegistroAdopcion
)

@admin.register(TipoMascota, EstadoMascota, Raza)
class SimpleAdmin(admin.ModelAdmin):
    list_display = ("id","nombre","activo","creado_en","actualizado_en")
    list_filter  = ("activo",)
    search_fields = ("nombre",)

class MascotaImagenInline(admin.TabularInline):
    model = MascotaImagen
    extra = 0

@admin.register(Mascota)
class MascotaAdmin(admin.ModelAdmin):
    list_display = ("id","nombre","tipo","raza","estado","activo","preview")
    list_filter  = ("tipo","estado","activo")
    search_fields = ("nombre","descripcion","raza__nombre","tipo__nombre")
    inlines = [MascotaImagenInline]
    readonly_fields = ("preview",)

    def preview(self, obj):
        if obj.foto_url:
            return mark_safe(f'<img src="{obj.foto_url.url}" style="height:80px;border-radius:8px;">')
        return "(sin imagen)"
    preview.short_description = "Foto"

@admin.register(MascotaImagen)
class MascotaImagenAdmin(admin.ModelAdmin):
    list_display = ("id","mascota","thumb","activo","creado_en")
    list_filter = ("activo",)
    search_fields = ("mascota__nombre",)

    def thumb(self, obj):
        if obj.imagen_url:
            return mark_safe(f'<img src="{obj.imagen_url.url}" style="height:60px;border-radius:6px;">')
        return "(sin imagen)"
    thumb.short_description = "Imagen"

@admin.register(PostulacionAdopcion)
class PostulacionAdmin(admin.ModelAdmin):
    list_display = ("id","mascota","nombres","apellidos","email","ciudad","activo","creado_en")
    list_filter = ("activo","ciudad")
    search_fields = ("nombres","apellidos","email","mascota__nombre")

@admin.register(RegistroAdopcion)
class RegistroAdopcionAdmin(admin.ModelAdmin):
    list_display = ("id","mascota","adoptante_nombre","fecha_adopcion","activo")
    list_filter = ("activo","fecha_adopcion")
    search_fields = ("adoptante_nombre","adoptante_doc","mascota__nombre")
