<?php

namespace App\Controllers\Api;

use App\Models\MenuModel;
use CodeIgniter\RESTful\ResourceController;

/**
 * MenuApi - CRUD REST de la tabla Menu (productos).
 *
 *   GET    /api/menu          -> index  (lista con categoria)
 *   GET    /api/menu/{id}     -> show
 *   POST   /api/menu          -> create
 *   PUT    /api/menu/{id}     -> update
 *   DELETE /api/menu/{id}     -> delete
 */
class MenuApi extends ResourceController
{
    protected $modelName = MenuModel::class;
    protected $format    = 'json';

    public function index()
    {
        return $this->respond([
            'status' => 'ok',
            'data'   => $this->model->obtenerProductosConCategoria(),
        ]);
    }

    public function show($id = null)
    {
        $producto = $this->model->find($id);

        if (! $producto) {
            return $this->failNotFound("No existe el producto con id $id.");
        }

        return $this->respond(['status' => 'ok', 'data' => $producto]);
    }

    public function create()
    {
        $data = $this->request->getJSON(true) ?? $this->request->getPost();

        if (! $this->model->insert($data)) {
            return $this->failValidationErrors($this->model->errors());
        }

        return $this->respondCreated([
            'status'  => 'ok',
            'message' => 'Producto creado correctamente.',
            'data'    => $data,
        ]);
    }

    public function update($id = null)
    {
        if (! $this->model->find($id)) {
            return $this->failNotFound("No existe el producto con id $id.");
        }

        $data = $this->request->getJSON(true) ?? $this->request->getRawInput();

        if (! $this->model->update($id, $data)) {
            return $this->failValidationErrors($this->model->errors());
        }

        return $this->respond([
            'status'  => 'ok',
            'message' => "Producto $id actualizado correctamente.",
        ]);
    }

    public function delete($id = null)
    {
        if (! $this->model->find($id)) {
            return $this->failNotFound("No existe el producto con id $id.");
        }

        $this->model->delete($id);

        return $this->respondDeleted([
            'status'  => 'ok',
            'message' => "Producto $id eliminado correctamente.",
        ]);
    }
}
