from django.db import models

class ActivoQuerySet(models.QuerySet):
    def activos(self): return self.filter(activo=True)

class TipoMascota(models.Model):
    nombre = models.CharField(max_length=30, unique=True)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    objects = ActivoQuerySet.as_manager()
    def __str__(self): return self.nombre

class EstadoMascota(models.Model):
    nombre = models.CharField(max_length=30, unique=True)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    objects = ActivoQuerySet.as_manager()
    def __str__(self): return self.nombre

class Raza(models.Model):
    tipo = models.ForeignKey(TipoMascota, on_delete=models.CASCADE, related_name="razas")
    nombre = models.CharField(max_length=60)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    objects = ActivoQuerySet.as_manager()
    class Meta: unique_together = ("tipo","nombre")
    def __str__(self): return f"{self.nombre} ({self.tipo.nombre})"

class Mascota(models.Model):
    nombre = models.CharField(max_length=120)
    tipo = models.ForeignKey(TipoMascota, on_delete=models.PROTECT)
    raza = models.ForeignKey(Raza, null=True, blank=True, on_delete=models.SET_NULL)
    edad_aprox = models.CharField(max_length=50, blank=True)
    tamano = models.CharField(max_length=50, blank=True)
    descripcion = models.TextField(blank=True)
    foto_url = models.ImageField(upload_to="mascotas/", blank=True, null=True)
    estado = models.ForeignKey(EstadoMascota, on_delete=models.PROTECT)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    objects = ActivoQuerySet.as_manager()
    def __str__(self): return self.nombre

class MascotaImagen(models.Model):
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE, related_name="imagenes")
    imagen_url = models.ImageField(upload_to="mascotas/")
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

class PostulacionAdopcion(models.Model):
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE, related_name="postulaciones")
    nombres = models.CharField(max_length=120)
    apellidos = models.CharField(max_length=120)
    dni_o_doc = models.CharField(max_length=20, blank=True)
    email = models.EmailField()
    telefono = models.CharField(max_length=30, blank=True)
    ciudad = models.CharField(max_length=100, blank=True)
    mensaje = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

class RegistroAdopcion(models.Model):
    mascota = models.OneToOneField(Mascota, on_delete=models.CASCADE)
    adoptante_nombre = models.CharField(max_length=200)
    adoptante_doc = models.CharField(max_length=20, blank=True)
    adoptante_ciudad = models.CharField(max_length=120)
    fecha_adopcion = models.DateField()
    observaciones = models.TextField(blank=True)
    id_usuario_registra = models.IntegerField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

