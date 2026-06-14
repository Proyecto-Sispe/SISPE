<?php

namespace App\Controllers\Api;

use App\Models\FacturaModel;
use CodeIgniter\RESTful\ResourceController;

/**
 * FacturaApi - REST de la tabla Factura.
 *
 *   GET    /api/facturas         -> index  (lista con cruce de tablas)
 *   GET    /api/facturas/{id}    -> show
 *   POST   /api/facturas         -> create
 *   DELETE /api/facturas/{id}    -> delete
 */
class FacturaApi extends ResourceController
{
    protected $modelName = FacturaModel::class;
    protected $format    = 'json';

    public function index()
    {
        $buscar = $this->request->getGet('buscar') ?? '';

        return $this->respond([
            'status' => 'ok',
            'data'   => $this->model->obtenerFacturas($buscar),
        ]);
    }

    public function show($id = null)
    {
        $factura = $this->model->find($id);

        if (! $factura) {
            return $this->failNotFound("No existe la factura con id $id.");
        }

        return $this->respond(['status' => 'ok', 'data' => $factura]);
    }

    public function create()
    {
        $data = $this->request->getJSON(true) ?? $this->request->getPost();

        $id = $this->model->insert($data);

        if (! $id) {
            return $this->failValidationErrors($this->model->errors());
        }

        return $this->respondCreated([
            'status'     => 'ok',
            'message'    => 'Factura creada correctamente.',
            'id_factura' => $id,
        ]);
    }

    public function delete($id = null)
    {
        if (! $this->model->find($id)) {
            return $this->failNotFound("No existe la factura con id $id.");
        }

        $this->model->delete($id);

        return $this->respondDeleted([
            'status'  => 'ok',
            'message' => "Factura $id eliminada correctamente.",
        ]);
    }
}
