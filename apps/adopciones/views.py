from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib import messages
from .models import Mascota, TipoMascota, Raza, PostulacionAdopcion
from django.conf import settings
from django.core.mail import send_mail

# -----------------------
# Helpers
# -----------------------

def _paginado(qs, request, per_page=12):
    return Paginator(qs, per_page).get_page(request.GET.get("page"))

def _context_listado(request, base_qs=None):
    """
    Construye el contexto para el listado (filtros, orden, paginación y combos).
    Si base_qs viene, se aplica como filtro base (ej. solo Perros o solo Gatos).
    """
    qs = base_qs if base_qs is not None else Mascota.objects.all()
    qs = qs.filter(activo=True)

    # Parámetros
    tipo_id = request.GET.get("tipo")
    raza_id = request.GET.get("raza")
    tam     = request.GET.get("tam")
    estado  = request.GET.get("estado")
    orden   = request.GET.get("o", "-id")
    q       = request.GET.get("q")  # búsqueda por nombre

    # Filtros
    if tipo_id:
        qs = qs.filter(tipo_id=tipo_id)
    if raza_id:
        qs = qs.filter(raza_id=raza_id)
    if tam:
        qs = qs.filter(tamano__iexact=tam)
    if estado:
        qs = qs.filter(estado__nombre__iexact=estado)
    if q:
        qs = qs.filter(nombre__icontains=q.strip())

    # Orden seguro
    allowed = {"-id", "id", "nombre", "-nombre", "-creado_en", "creado_en"}
    if orden not in allowed:
        orden = "-id"
    qs = qs.order_by(orden)

    # Paginación
    page = _paginado(qs, request)

    # Combos
    tipos = TipoMascota.objects.filter(activo=True).order_by("nombre")

    razas_qs = Raza.objects.filter(activo=True)
    if tipo_id:
        # Si Raza NO tiene FK a TipoMascota, comenta/borra la siguiente línea:
        razas_qs = razas_qs.filter(tipo_id=tipo_id)
    razas = razas_qs.order_by("nombre")

    tamanos = (
        Mascota.objects
        .exclude(tamano__isnull=True)
        .exclude(tamano__exact="")
        .values_list("tamano", flat=True)
        .distinct()
        .order_by("tamano")
    )

    estados = ["Disponible", "Adoptado"]

    ctx = {
        "mascotas": page,
        "tipos": tipos,
        "razas": razas,
        "tamanos": tamanos,
        "estados": estados,
        "params": {
            "tipo": tipo_id,
            "raza": raza_id,
            "tam": tam,
            "estado": estado,
            "o": orden,
            "q": q or "",
        },
    }
    return ctx

# -----------------------
# Vistas
# -----------------------

def listado(request):
    ctx = _context_listado(request)
    return render(request, "adopciones/listado.html", ctx)

def listado_wufs(request):
    # Perros
    base = Mascota.objects.filter(tipo__nombre__iexact="Perro")
    ctx = _context_listado(request, base_qs=base)
    return render(request, "adopciones/listado.html", ctx)

def listado_miaus(request):
    # Gatos
    base = Mascota.objects.filter(tipo__nombre__iexact="Gato")
    ctx = _context_listado(request, base_qs=base)
    return render(request, "adopciones/listado.html", ctx)

def detalle(request, pk):
    mascota = get_object_or_404(Mascota, pk=pk, activo=True)
    return render(request, "adopciones/detalle.html", {"mascota": mascota})

def postular(request, pk):
    mascota = get_object_or_404(Mascota, pk=pk, activo=True)

    if request.method == "POST":
        nombres   = request.POST.get("nombres","").strip()
        apellidos = request.POST.get("apellidos","").strip()
        email     = request.POST.get("email","").strip()
        telefono  = request.POST.get("telefono","").strip()
        ciudad    = request.POST.get("ciudad","").strip()
        mensaje   = request.POST.get("mensaje","").strip()

        if not (nombres and apellidos and email):
            messages.error(request, "Completa al menos nombres, apellidos y email.")
            return redirect("adopta_postular", pk=pk)

        postulacion = PostulacionAdopcion.objects.create(
            mascota=mascota,
            nombres=nombres,
            apellidos=apellidos,
            email=email,
            telefono=telefono,
            ciudad=ciudad,
            mensaje=mensaje,
            activo=True
        )

        # --- (3) Envío de correos ---
        try:
            de = getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@huellasolidaria.local")
            para_equipo = [getattr(settings, "ADOPCIONES_EMAIL", de)]

            # Aviso al equipo
            asunto_admin = f"[Adopciones] Nueva postulación para {mascota.nombre}"
            cuerpo_admin = (
                f"Se registró una nueva postulación.\n\n"
                f"Mascota: {mascota.nombre}\n"
                f"Postulante: {nombres} {apellidos}\n"
                f"Email: {email}\n"
                f"Teléfono: {telefono}\n"
                f"Ciudad: {ciudad}\n\n"
                f"Mensaje:\n{mensaje}\n"
            )
            send_mail(asunto_admin, cuerpo_admin, de, para_equipo, fail_silently=True)

            # Confirmación al postulante
            asunto_user = f"¡Gracias por postular a {mascota.nombre}!"
            cuerpo_user = (
                f"Hola {nombres},\n\n"
                f"Gracias por tu interés en {mascota.nombre}. Nuestro equipo revisará tu postulación "
                f"y se pondrá en contacto contigo pronto.\n\n"
                f"– Huella Solidaria"
            )
            if email:
                send_mail(asunto_user, cuerpo_user, de, [email], fail_silently=True)
        except Exception:
            # No rompemos el flujo si el correo falla
            pass

        # (1) Pantalla de confirmación
        return render(request, "adopciones/postulacion_exito.html", {
            "mascota": mascota,
            "postulacion": postulacion,
        })

    return render(request, "adopciones/postular.html", {"mascota": mascota})

# -----------------------
# API (AJAX) - RAZAS POR TIPO
# -----------------------

def api_razas(request):
    """Devuelve razas activas, opcionalmente filtradas por tipo_id."""
    tipo_id = request.GET.get("tipo")
    razas_qs = Raza.objects.filter(activo=True)
    if tipo_id:
        # Si tu modelo Raza NO tiene FK a TipoMascota, comenta la línea siguiente
        razas_qs = razas_qs.filter(tipo_id=tipo_id)
    data = list(razas_qs.order_by("nombre").values("id", "nombre"))
    return JsonResponse(data, safe=False)

def razas_por_tipo(request):
    """
    Devuelve razas activas filtradas por ?tipo=<id> en JSON.
    """
    tipo_id = request.GET.get("tipo")
    qs = Raza.objects.filter(activo=True)
    if tipo_id:
        # Si Raza no tiene FK a TipoMascota, comenta la siguiente línea.
        qs = qs.filter(tipo_id=tipo_id)
    data = [{"id": r.id, "nombre": r.nombre} for r in qs.order_by("nombre")]
    return JsonResponse({"razas": data})
