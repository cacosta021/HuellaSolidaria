from django.db import models

class MetodoDonacion(models.Model):
    nombre = models.CharField(max_length=40, unique=True)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    def __str__(self): return self.nombre

class Donacion(models.Model):
    # ← NUEVO: vínculo opcional a Perro/Gato (TipoMascota de adopciones)
    tipo = models.ForeignKey(
        'adopciones.TipoMascota',
        on_delete=models.PROTECT,
        related_name='donaciones',
        null=True, blank=True
    )
    nombre = models.CharField(max_length=120, blank=True, null=True)
    email  = models.EmailField(blank=True, null=True)
    monto  = models.DecimalField(max_digits=10, decimal_places=2)
    metodo = models.ForeignKey(MetodoDonacion, on_delete=models.PROTECT)
    mensaje = models.TextField(blank=True, null=True)
    activo  = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    def __str__(self): return f"{self.nombre or 'Anónimo'} - {self.monto}"
