<?php

namespace App\Controllers\Api;

use App\Models\MesaModel;
use CodeIgniter\RESTful\ResourceController;

/**
 * MesaApi - CRUD REST de la tabla Mesa.
 *
 * Rutas (definidas como resource en Routes.php):
 *   GET    /api/mesas            -> index   (listar)
 *   GET    /api/mesas/{id}       -> show     (detalle)
 *   POST   /api/mesas            -> create   (crear)
 *   PUT    /api/mesas/{id}       -> update   (actualizar)
 *   DELETE /api/mesas/{id}       -> delete   (eliminar)
 */
class MesaApi extends ResourceController
{
    protected $modelName = MesaModel::class;
    protected $format    = 'json';

    public function index()
    {
        return $this->respond([
            'status' => 'ok',
            'data'   => $this->model->orderBy('id_Mesa', 'ASC')->findAll(),
        ]);
    }

    public function show($id = null)
    {
        $mesa = $this->model->find($id);

        if (! $mesa) {
            return $this->failNotFound("No existe la mesa con id $id.");
        }

        return $this->respond(['status' => 'ok', 'data' => $mesa]);
    }

    public function create()
    {
        $data = $this->request->getJSON(true) ?? $this->request->getPost();

        if (! $this->model->insert($data)) {
            return $this->failValidationErrors($this->model->errors());
        }

        return $this->respondCreated([
            'status'  => 'ok',
            'message' => 'Mesa creada correctamente.',
            'data'    => $data,
        ]);
    }

    public function update($id = null)
    {
        if (! $this->model->find($id)) {
            return $this->failNotFound("No existe la mesa con id $id.");
        }

        $data = $this->request->getJSON(true) ?? $this->request->getRawInput();

        if (! $this->model->update($id, $data)) {
            return $this->failValidationErrors($this->model->errors());
        }

        return $this->respond([
            'status'  => 'ok',
            'message' => "Mesa $id actualizada correctamente.",
        ]);
    }

    public function delete($id = null)
    {
        if (! $this->model->find($id)) {
            return $this->failNotFound("No existe la mesa con id $id.");
        }

        $this->model->delete($id);

        return $this->respondDeleted([
            'status'  => 'ok',
            'message' => "Mesa $id eliminada correctamente.",
        ]);
    }
}
