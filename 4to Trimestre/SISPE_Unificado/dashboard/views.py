from django.shortcuts import redirect


def inicio(request):
    return redirect("reportes")