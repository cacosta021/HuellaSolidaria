from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.db.utils import OperationalError
from .models import Post

def listado(request):
    posts = []
    try:
        posts = Post.objects.filter(publicado=True).order_by('-creado_en')[:10]
    except OperationalError:
        # Si no existe la tabla todavía, no rompas la página
        posts = []
    return render(request, "blog/listado.html", {"posts": posts})

def detalle(request, slug):
    try:
        post = get_object_or_404(Post, slug=slug, publicado=True)
    except OperationalError:
        # Si no hay tabla del blog aún
        raise Http404("El blog todavía no está disponible.")
    return render(request, "blog/detalle.html", {"post": post})
