<?php

namespace App\Controllers;

class InicioController extends BaseController
{
    // Pagina de inicio publica (landing). No requiere iniciar sesion.
    public function index()
    {
        return view('inicio');
    }
}