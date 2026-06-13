<?php

namespace App\Controllers\Api;

use App\Controllers\BaseController;
use CodeIgniter\API\ResponseTrait;
use CodeIgniter\Database\Config;

/**
 * AuthApi
 *
 * Endpoint de autenticacion para consumir desde Postman.
 * Valida el correo y la contrasena contra la tabla Persona y
 * devuelve los datos del usuario junto a su rol en formato JSON.
 */
class AuthApi extends BaseController
{
    use ResponseTrait;

    /**
     * POST /api/login
     * Body (JSON o x-www-form-urlencoded): { "email": "...", "password": "..." }
     */
    public function login()
    {
        // getJSON / getPost: admite tanto JSON como formularios
        $data     = $this->request->getJSON(true) ?? $this->request->getPost();
        $email    = trim($data['email'] ?? '');
        $password = trim($data['password'] ?? '');

        if ($email === '' || $password === '') {
            return $this->failValidationErrors('El correo y la contrasena son obligatorios.');
        }

        $db = Config::connect();

        $sql = "SELECT p.id_usuario, p.pkfk_Tipo_doc, p.Nom1_usu, p.Ape1_usu,
                       p.Correo_usu, p.Password, r.Nom_rol
                FROM Persona p
                INNER JOIN Persona_has_Rol phr
                    ON p.id_usuario = phr.pkfk_id_usuario
                   AND p.pkfk_Tipo_doc = phr.pkfk_Tipo_doc
                INNER JOIN Rol r ON phr.pkfk_idRol = r.idRol
                WHERE p.Correo_usu = ? AND p.estado = 1";

        $usuario = $db->query($sql, [$email])->getRowArray();

        if (! $usuario) {
            return $this->failNotFound('El usuario no existe o esta inactivo.');
        }

        // Acepta hash seguro o el texto plano '1234' de los datos de ejemplo
        $passwordOk = password_verify($password, $usuario['Password'])
            || $password === $usuario['Password'];

        if (! $passwordOk) {
            return $this->failUnauthorized('Contrasena incorrecta.');
        }

        unset($usuario['Password']);

        return $this->respond([
            'status'  => 'ok',
            'message' => 'Autenticacion exitosa',
            'usuario' => $usuario,
        ]);
    }
}
