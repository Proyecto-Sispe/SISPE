<?php

namespace App\Controllers\Api;

use App\Models\PedidoModel;
use CodeIgniter\RESTful\ResourceController;

/**
 * PedidoApi - CRUD REST de la tabla Pedido.
 *
 *   GET    /api/pedidos         -> index
 *   GET    /api/pedidos/{id}    -> show
 *   POST   /api/pedidos         -> create
 *   PUT    /api/pedidos/{id}    -> update
 *   DELETE /api/pedidos/{id}    -> delete
 */
class PedidoApi extends ResourceController
{
    protected $modelName = PedidoModel::class;
    protected $format    = 'json';

    public function index()
    {
        return $this->respond([
            'status' => 'ok',
            'data'   => $this->model->orderBy('fecha_pedido', 'DESC')->findAll(),
        ]);
    }

    public function show($id = null)
    {
        $pedido = $this->model->find($id);

        if (! $pedido) {
            return $this->failNotFound("No existe el pedido con id $id.");
        }

        return $this->respond(['status' => 'ok', 'data' => $pedido]);
    }

    public function create()
    {
        $data = $this->request->getJSON(true) ?? $this->request->getPost();

        $id = $this->model->insert($data);

        if (! $id) {
            return $this->failValidationErrors($this->model->errors());
        }

        return $this->respondCreated([
            'status'    => 'ok',
            'message'   => 'Pedido creado correctamente.',
            'id_pedido' => $id,
        ]);
    }

    public function update($id = null)
    {
        if (! $this->model->find($id)) {
            return $this->failNotFound("No existe el pedido con id $id.");
        }

        $data = $this->request->getJSON(true) ?? $this->request->getRawInput();

        if (! $this->model->update($id, $data)) {
            return $this->failValidationErrors($this->model->errors());
        }

        return $this->respond([
            'status'  => 'ok',
            'message' => "Pedido $id actualizado correctamente.",
        ]);
    }

    public function delete($id = null)
    {
        if (! $this->model->find($id)) {
            return $this->failNotFound("No existe el pedido con id $id.");
        }

        $this->model->delete($id);

        return $this->respondDeleted([
            'status'  => 'ok',
            'message' => "Pedido $id eliminado correctamente.",
        ]);
    }
}
