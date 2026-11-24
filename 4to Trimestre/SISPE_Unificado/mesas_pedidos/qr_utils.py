from io import BytesIO
from django.core.files.base import ContentFile
from django.urls import reverse
import qrcode


def generar_qr_mesa(mesa, request):
    url_relativa = reverse("escanear_mesa", kwargs={"id_mesa": mesa.id})
    url_completa = request.build_absolute_uri(url_relativa)

    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(url_completa)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")

    nombre_archivo = f"qr_mesa_{mesa.id}.png"
    mesa.qr_imagen.save(nombre_archivo, ContentFile(buffer.getvalue()), save=True)