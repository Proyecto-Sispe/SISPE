"""Generacion de codigos QR en el propio servidor (sin depender de internet)."""

import io

try:  # preferido: segno, puro Python, sin compilador
    import segno

    _MOTOR = "segno"
except ImportError:  # pragma: no cover
    segno = None
    try:
        import qrcode

        _MOTOR = "qrcode"
    except ImportError:
        qrcode = None
        _MOTOR = None


def motor():
    return _MOTOR


def url_carta(host, mesa):
    host = (host or "127.0.0.1:8000").strip().rstrip("/")
    if not host.startswith("http"):
        host = "http://" + host
    return f"{host}/servicio/mesa/{mesa}/pedir/"


def generar_png(texto):
    """Devuelve los bytes PNG del QR, o None si no hay motor disponible."""
    if segno is not None:
        buffer = io.BytesIO()
        qr = segno.make(texto, error="m")
        qr.save(buffer, kind="png", scale=8, border=2, dark="#14100e", light="#ffffff")
        return buffer.getvalue()

    if qrcode is not None:  # pragma: no cover
        qr = qrcode.QRCode(box_size=8, border=2)
        qr.add_data(texto)
        qr.make(fit=True)
        imagen = qr.make_image(fill_color="#14100e", back_color="white")
        buffer = io.BytesIO()
        imagen.save(buffer, format="PNG")
        return buffer.getvalue()

    return None


def data_uri(texto):
    """QR como data URI para incrustarlo directo en el HTML."""
    import base64

    png = generar_png(texto)
    if not png:
        return None
    return "data:image/png;base64," + base64.b64encode(png).decode("ascii")


def url_respaldo(texto, tamano=260):
    """Ultimo recurso: servicio externo, solo si no hay motor local."""
    from urllib.parse import quote

    return (
        "https://pageloot.com/wp-content/uploads/2026/09/aspect-ratio-1-1-simple-clean-infographic-on-a-white-background-with-black-text-2966-3fd2d44c9e77-971f39871103.webp"
        f"?size={tamano}x{tamano}&data={quote(texto)}"
    )
