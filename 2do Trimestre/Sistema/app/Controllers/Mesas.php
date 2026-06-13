<?php

namespace App\Controllers;

use App\Models\MesaModel;

class Mesas extends BaseController
{
    // Listado en Grid (Tu Mesas 2.Html)
    public function index()
    {
        $mesaModel = new MesaModel();
        $data['mesas'] = $mesaModel->findAll();
        return view('mesas/mesas_listado', $data);
    }

    // Formulario de Agregar (Tu Agregar Mesa.Html)
    public function agregar()
    {
        return view('mesas/agregar_mesa');
    }

    // Guardar nueva mesa
    public function guardar()
    {
        $mesaModel = new MesaModel();
        $mesaModel->insert([
            'id_Mesa'   => $this->request->getPost('id_mesa'),
            'Capacidad' => $this->request->getPost('capacidad'),
            'Ubicacion' => $this->request->getPost('ubicacion'),
            'Estado'    => 0
        ]);
        return redirect()->to(base_url('mesas'));
    }

    // =============================================================================
    // NUEVAS FUNCIONES: EDITAR Y ELIMINAR
    // =============================================================================

    // Carga el formulario de edición con los datos actuales de la mesa elegida
    public function editar($id)
    {
        $mesaModel = new MesaModel();
        $data['mesa'] = $mesaModel->find($id);

        if (!$data['mesa']) {
            return "La mesa que intentas editar no existe.";
        }

        return view('mesas/editar_mesa', $data);
    }

    // Procesa los cambios en la base de datos
    public function actualizar()
    {
        $mesaModel = new MesaModel();
        $id_mesa = $this->request->getPost('id_mesa');

        $mesaModel->update($id_mesa, [
            'Capacidad' => $this->request->getPost('capacidad'),
            'Ubicacion' => $this->request->getPost('ubicacion'),
            'Estado'    => $this->request->getPost('estado') // Permite cambiar si está libre u ocupada manualmente
        ]);

        return redirect()->to(base_url('mesas'));
    }

    // Llama al procedimiento almacenado y elimina la mesa por completo
    public function eliminar($id)
    {
        $db = \Config\Database::connect();
        
        try {
            // Ejecutamos el procedimiento almacenado seguro que creamos en MySQL
            $db->query("CALL EliminarMesaSegura(?)", [$id]);
            return redirect()->to(base_url('mesas'));
        } catch (\Exception $e) {
            return "Error al eliminar la mesa: " . $e->getMessage();
        }
    }
}

