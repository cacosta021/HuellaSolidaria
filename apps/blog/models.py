from django.db import models

class Post(models.Model):
    titulo = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    contenido = models.TextField()
    publicado = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "blog_post"   # ← coincide con el nombre que reclama el error
        ordering = ["-creado_en"]

    def __str__(self):
        return self.titulo
