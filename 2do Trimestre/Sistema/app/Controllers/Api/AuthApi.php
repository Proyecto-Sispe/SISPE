<?php

namespace App\Controllers\Api;

use App\Controllers\BaseController;
use App\Models\PasswordResetModel;
use App\Models\PersonaModel;
use CodeIgniter\API\ResponseTrait;
use CodeIgniter\Database\Config;

/**
 * AuthApi
 *
 * Endpoint de autenticacion para consumir desde Postman.
 * Valida el correo y la contrasena contra la tabla Persona y
 * devuelve los datos del usuario junto a su rol en formato JSON.
  * Endpoints de autenticacion para consumir desde Postman:
 *   - POST /api/login            Inicio de sesion
 *   - POST /api/forgot-password  Solicita el correo de recuperacion
 *   - POST /api/reset-password   Cambia la contrasena con el token/codigo
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
    /**
     * POST /api/forgot-password
     * Body: { "email": "usuario@correo.com" }
     *
     * Genera un token + codigo de 6 digitos, lo guarda en `password_resets`
     * y envia un correo al usuario con las instrucciones para restablecer.
     */
    public function forgotPassword()
    {
        $data  = $this->request->getJSON(true) ?? $this->request->getPost();
        $email = trim($data['email'] ?? '');

        if ($email === '') {
            return $this->failValidationErrors('El correo es obligatorio.');
        }

        $personaModel = new PersonaModel();
        $usuario      = $personaModel->where('Correo_usu', $email)
                                     ->where('estado', 1)
                                     ->first();

        // Respuesta neutra: no revelamos si el correo existe (evita enumeracion)
        $respuestaNeutra = [
            'status'  => 'ok',
            'message' => 'Si el correo esta registrado, recibiras un mensaje con las instrucciones.',
        ];

        if (! $usuario) {
            return $this->respond($respuestaNeutra);
        }

        // Genera token (para enlace) y codigo de 6 digitos (para ingresar manualmente)
        $token  = bin2hex(random_bytes(32));
        $codigo = str_pad((string) random_int(0, 999999), 6, '0', STR_PAD_LEFT);

        $resetModel = new PasswordResetModel();

        // Invalida tokens anteriores del mismo correo
        $resetModel->where('correo', $email)->set(['usado' => 1])->update();

        $resetModel->insert([
            'correo'     => $email,
            'token'      => hash('sha256', $token),
            'codigo'     => $codigo,
            'expira'     => date('Y-m-d H:i:s', strtotime('+15 minutes')),
            'usado'      => 0,
            'created_at' => date('Y-m-d H:i:s'),
        ]);

        // Enlace de recuperacion (ajusta la ruta del front si aplica)
        $enlace = base_url('reset-password?token=' . $token);

        $nombre = trim(($usuario['Nom1_usu'] ?? '') . ' ' . ($usuario['Ape1_usu'] ?? ''));
        $cuerpo = $this->plantillaCorreo($nombre, $codigo, $enlace);

        $emailService = \Config\Services::email();
        $emailService->setTo($email);
        $emailService->setSubject('Recuperacion de contrasena - SISPE');
        $emailService->setMessage($cuerpo);
        $emailService->setMailType('html');

        if (! $emailService->send(false)) {
            // En desarrollo devolvemos el detalle para depurar el SMTP
            return $this->failServerError(
                'No se pudo enviar el correo. Revisa la configuracion SMTP. '
                . $emailService->printDebugger(['headers'])
            );
        }

        return $this->respond($respuestaNeutra);
    }

    /**
     * POST /api/reset-password
     * Body: { "token": "...", "password": "nueva", "password_confirm": "nueva" }
     *   o:  { "email": "...", "codigo": "123456", "password": "nueva", "password_confirm": "nueva" }
     */
    public function resetPassword()
    {
        $data            = $this->request->getJSON(true) ?? $this->request->getPost();
        $token           = trim($data['token'] ?? '');
        $email           = trim($data['email'] ?? '');
        $codigo          = trim($data['codigo'] ?? '');
        $password        = trim($data['password'] ?? '');
        $passwordConfirm = trim($data['password_confirm'] ?? '');

        if ($password === '' || strlen($password) < 4) {
            return $this->failValidationErrors('La contrasena debe tener al menos 4 caracteres.');
        }

        if ($password !== $passwordConfirm) {
            return $this->failValidationErrors('Las contrasenas no coinciden.');
        }

        if ($token === '' && ($email === '' || $codigo === '')) {
            return $this->failValidationErrors('Debes enviar el token, o el correo junto al codigo.');
        }

        $resetModel = new PasswordResetModel();
        $builder    = $resetModel->where('usado', 0)
                                 ->where('expira >=', date('Y-m-d H:i:s'));

        if ($token !== '') {
            $builder->where('token', hash('sha256', $token));
        } else {
            $builder->where('correo', $email)->where('codigo', $codigo);
        }

        $registro = $builder->orderBy('id', 'DESC')->first();

        if (! $registro) {
            return $this->failValidationErrors('El token o codigo es invalido o ya expiro.');
        }

        // Actualiza la contrasena del usuario (hash seguro)
        $personaModel = new PersonaModel();
        $usuario      = $personaModel->where('Correo_usu', $registro['correo'])->first();

        if (! $usuario) {
            return $this->failNotFound('El usuario asociado no existe.');
        }

        $personaModel->set('Password', password_hash($password, PASSWORD_DEFAULT))
                     ->where('id_usuario', $usuario['id_usuario'])
                     ->where('pkfk_Tipo_doc', $usuario['pkfk_Tipo_doc'])
                     ->update();

        // Marca el token como usado
        $resetModel->update($registro['id'], ['usado' => 1]);

        return $this->respond([
            'status'  => 'ok',
            'message' => 'La contrasena se actualizo correctamente.',
        ]);
    }

    /**
     * Plantilla HTML simple para el correo de recuperacion.
     */
    private function plantillaCorreo(string $nombre, string $codigo, string $enlace): string
    {
        return '
            <div style="font-family:Arial,sans-serif;max-width:480px;margin:auto;color:#1f2937">
                <h2 style="color:#b91c1c">SISPE - Recuperacion de contrasena</h2>
                <p>Hola ' . esc($nombre) . ',</p>
                <p>Recibimos una solicitud para restablecer tu contrasena. Usa el siguiente codigo:</p>
                <p style="font-size:28px;font-weight:bold;letter-spacing:4px;color:#b91c1c">' . esc($codigo) . '</p>
                <p>O haz clic en el siguiente enlace (valido por 15 minutos):</p>
                <p><a href="' . esc($enlace, 'attr') . '" style="background:#b91c1c;color:#fff;padding:10px 18px;border-radius:6px;text-decoration:none">Restablecer contrasena</a></p>
                <p style="font-size:12px;color:#6b7280">Si no solicitaste este cambio, ignora este mensaje.</p>
            </div>
        ';
    }
}
