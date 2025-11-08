import io
import base64
import qrcode
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from django.contrib import messages
from django.shortcuts import render
from apps.adopciones.models import TipoMascota, Mascota
from apps.donaciones.models import MetodoDonacion, Donacion


def donar(request):
    """
    Página de donaciones:
    - GET: muestra el formulario. Soporta ?from=<origen>&pet=<id_mascota> para mensajes contextuales.
    - POST: valida datos, genera QR (placeholder), guarda registro y devuelve modal con QR.
    """
    metodos = MetodoDonacion.objects.filter(activo=True).order_by("nombre")
    tipos = TipoMascota.objects.filter(activo=True).order_by("nombre")

    # --- Contexto opcional: origen y mascota (para mensaje inspiracional) ---
    origen = (request.GET.get("from") or "").strip()  # p.ej. 'adopciones'
    pet_nombre = None
    pet_id = (request.GET.get("pet") or "").strip()
    if pet_id:
        try:
            pet_nombre = Mascota.objects.values_list("nombre", flat=True).get(pk=pet_id)
        except Mascota.DoesNotExist:
            pet_nombre = None  # no rompemos la vista si no existe

    qr_png = None
    form_vals = {}

    if request.method == "POST":
        metodo_id = (request.POST.get("metodo") or "").strip()
        tipo_id = (request.POST.get("tipo") or "").strip() or None
        monto_raw = (request.POST.get("monto") or "").strip()

        # --- Validación y normalización del monto ---
        try:
            monto = Decimal(monto_raw)
            if monto <= 0:
                raise InvalidOperation
            # redondeo a 2 decimales (bancario)
            monto = monto.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        except (InvalidOperation, TypeError, ValueError):
            messages.error(request, "Ingresa un monto válido mayor a 0.")
            form_vals = {"metodo": metodo_id, "tipo": tipo_id, "monto": monto_raw}
            return render(
                request,
                "donaciones/donar.html",
                {
                    "metodos": metodos,
                    "tipos": tipos,
                    "qr_png": None,
                    "form_vals": form_vals,
                    "pet_nombre": pet_nombre,
                    "origen": origen,
                },
            )

        # --- Validación del método ---
        try:
            metodo = MetodoDonacion.objects.get(pk=metodo_id, activo=True)
        except MetodoDonacion.DoesNotExist:
            messages.error(request, "Selecciona un método de donación válido.")
            form_vals = {"metodo": metodo_id, "tipo": tipo_id, "monto": str(monto)}
            return render(
                request,
                "donaciones/donar.html",
                {
                    "metodos": metodos,
                    "tipos": tipos,
                    "qr_png": None,
                    "form_vals": form_vals,
                    "pet_nombre": pet_nombre,
                    "origen": origen,
                },
            )

        # --- Tipo (opcional) ---
        tipo = None
        if tipo_id:
            tipo = TipoMascota.objects.filter(pk=tipo_id, activo=True).first()

        # --- Construcción del payload (placeholder) ---
        # Aquí luego puedes implementar el estándar exacto de Yape/Plin si lo deseas.
        payload = (
            f"ORIGEN={origen or 'web'}|"
            f"METODO={metodo.nombre}|"
            f"MONTO=S/{monto}|"
            f"TIPO={tipo.nombre if tipo else 'General'}|"
            f"PET={pet_nombre or ''}"
        )

        # --- Generación del QR ---
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=2,
        )
        qr.add_data(payload)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        qr_png = base64.b64encode(buffer.getvalue()).decode()

        # --- Guardar donación ---
        # Puedes ajustar estos campos según tu modelo
        Donacion.objects.create(
            tipo=tipo,
            nombre="Anónimo",
            monto=monto,
            metodo=metodo,
            mensaje=(
                f"Donación generada desde la web"
                f"{f' (origen: {origen})' if origen else ''}"
                f"{f' para {pet_nombre}' if pet_nombre else ''}"
            ),
        )

        messages.success(
            request,
            "¡Gracias por tu donación! Escanea el QR para completar el pago.",
        )
        form_vals = {"metodo": metodo_id, "tipo": tipo_id or "", "monto": str(monto)}

    else:
        # GET inicial (intenta preseleccionar un método si solo hay uno)
        form_vals = {}
        if metodos.count() == 1:
            form_vals["metodo"] = str(metodos.first().id)

    return render(
        request,
        "donaciones/donar.html",
        {
            "metodos": metodos,
            "tipos": tipos,
            "qr_png": qr_png,
            "form_vals": form_vals,
            "pet_nombre": pet_nombre,
            "origen": origen,
        },
    )
