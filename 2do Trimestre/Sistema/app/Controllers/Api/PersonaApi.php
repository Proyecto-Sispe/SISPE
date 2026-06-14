<?php

namespace App\Controllers\Api;

use App\Models\PersonaModel;
use CodeIgniter\RESTful\ResourceController;

/**
 * PersonaApi - REST de la tabla Persona (usuarios).
 *
 * Nota: la tabla Persona usa llave compuesta (id_usuario, pkfk_Tipo_doc),
 * pero para la API usamos id_usuario como identificador en la URL.
 *
 *   GET    /api/personas         -> index
 *   GET    /api/personas/{id}    -> show
 *   POST   /api/personas         -> create
 *   PUT    /api/personas/{id}    -> update
 *   DELETE /api/personas/{id}    -> delete
 */
class PersonaApi extends ResourceController
{
    protected $modelName = PersonaModel::class;
    protected $format    = 'json';

    public function index()
    {
        $personas = $this->model->orderBy('Nom1_usu', 'ASC')->findAll();

        // Nunca devolvemos la contrasena en la respuesta
        foreach ($personas as &$p) {
            unset($p['Password']);
        }

        return $this->respond(['status' => 'ok', 'data' => $personas]);
    }

    public function show($id = null)
    {
        $persona = $this->model->where('id_usuario', $id)->first();

        if (! $persona) {
            return $this->failNotFound("No existe la persona con id $id.");
        }

        unset($persona['Password']);

        return $this->respond(['status' => 'ok', 'data' => $persona]);
    }

    public function create()
    {
        $data = $this->request->getJSON(true) ?? $this->request->getPost();

        // Hashea la contrasena si viene en el cuerpo
        if (! empty($data['Password'])) {
            $data['Password'] = password_hash($data['Password'], PASSWORD_DEFAULT);
        }

        if (! $this->model->insert($data)) {
            return $this->failValidationErrors($this->model->errors());
        }

        return $this->respondCreated([
            'status'  => 'ok',
            'message' => 'Persona creada correctamente.',
        ]);
    }

    public function update($id = null)
    {
        $persona = $this->model->where('id_usuario', $id)->first();

        if (! $persona) {
            return $this->failNotFound("No existe la persona con id $id.");
        }

        $data = $this->request->getJSON(true) ?? $this->request->getRawInput();

        if (! empty($data['Password'])) {
            $data['Password'] = password_hash($data['Password'], PASSWORD_DEFAULT);
        }

        // Actualiza usando la llave compuesta real del registro encontrado
        $this->model->where('id_usuario', $persona['id_usuario'])
                    ->where('pkfk_Tipo_doc', $persona['pkfk_Tipo_doc'])
                    ->set($data)
                    ->update();

        return $this->respond([
            'status'  => 'ok',
            'message' => "Persona $id actualizada correctamente.",
        ]);
    }

    public function delete($id = null)
    {
        $persona = $this->model->where('id_usuario', $id)->first();

        if (! $persona) {
            return $this->failNotFound("No existe la persona con id $id.");
        }

        $this->model->where('id_usuario', $persona['id_usuario'])
                    ->where('pkfk_Tipo_doc', $persona['pkfk_Tipo_doc'])
                    ->delete();

        return $this->respondDeleted([
            'status'  => 'ok',
            'message' => "Persona $id eliminada correctamente.",
        ]);
    }
}
