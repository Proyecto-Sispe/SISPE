<?php

namespace App\Controllers;

use App\Controllers\BaseController;
use App\Models\AdminPersonaModel;
use App\Models\FacturaModel;
use App\Models\MenuModel;
use Dompdf\Dompdf;
use Dompdf\Options;

class ReporteController extends BaseController
{
    public function index()
    {
        if (session('rol') !== 'Administrador') {
            return redirect()->to('dashboard')->with('error', 'Acceso denegado');
        }

        return view('reportes/index');
    }

    public function pdfVentas()
    {
        if (session('rol') !== 'Administrador') {
            return redirect()->to('dashboard')->with('error', 'Acceso denegado');
        }

        $facturaModel = new FacturaModel();
        $facturas = $facturaModel->obtenerFacturas();

        $totalGeneral = 0;
        foreach ($facturas as $factura) {
            $totalGeneral += floatval($factura['Total']);
        }

        $data['titulo'] = "Reporte Específico de Ventas - Facturas";
        $data['fecha'] = date('d/m/Y');
        $data['hora'] = date('H:i:s');
        $data['facturas'] = $facturas;
        $data['totalGeneral'] = $totalGeneral;

        $options = new Options();
        $options->set('isHtml5ParserEnabled', true);
        $options->set('isRemoteEnabled', true);

        $dompdf = new Dompdf($options);
        $html = view('reportes/pdf_ventas', $data);
        $dompdf->loadHtml($html);
        $dompdf->setPaper('A4', 'portrait');
        $dompdf->render();
        $dompdf->stream('reporte_ventas.pdf', ['Attachment' => false]);
    }

    public function pdfProductos()
    {
        if (session('rol') !== 'Administrador') {
            return redirect()->to('dashboard')->with('error', 'Acceso denegado');
        }

        $menuModel = new MenuModel();
        $data['titulo'] = "Reporte de Productos - Sistema de Gestión";
        $data['fecha'] = date('d/m/Y');
        $data['hora'] = date('H:i:s');
        $data['productos'] = $menuModel->obtenerProductosConCategoria();

        $options = new Options();
        $options->set('isHtml5ParserEnabled', true);
        $options->set('isRemoteEnabled', true);

        $dompdf = new Dompdf($options);
        $html = view('reportes/pdf_productos', $data);
        $dompdf->loadHtml($html);
        $dompdf->setPaper('A4', 'portrait');
        $dompdf->render();
        $dompdf->stream('reporte_productos.pdf', ['Attachment' => false]);
    }

    public function pdfUsuarios()
    {
        if (session('rol') !== 'Administrador') {
            return redirect()->to('dashboard')->with('error', 'Acceso denegado');
        }

        $personaModel = new AdminPersonaModel();
        $data['titulo'] = 'Reporte de Usuarios - Sistema de Gestión';
        $data['fecha'] = date('d/m/Y');
        $data['hora'] = date('H:i:s');
        $data['usuarios'] = $personaModel->obtenerUsuarios();

        $options = new Options();
        $options->set('isHtml5ParserEnabled', true);
        $options->set('isRemoteEnabled', true);

        $dompdf = new Dompdf($options);
        $html = view('reportes/pdf_usuarios', $data);
        $dompdf->loadHtml($html);
        $dompdf->setPaper('A4', 'portrait');
        $dompdf->render();
        $dompdf->stream('reporte_usuarios.pdf', ['Attachment' => false]);
    }
}