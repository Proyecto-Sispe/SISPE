<?php

namespace App\Controllers;

use App\Models\PasswordResetModel;
use App\Models\PersonaModel;

/**
 * PasswordController
 *
 * Flujo web para "Olvide mi contrasena":
 *   GET  /olvide-password    Muestra el formulario para pedir el correo
 *   POST /olvide-password    Genera el codigo/token y envia el correo
 *   GET  /reset-password     Muestra el formulario para ingresar el codigo y la nueva clave
 *   POST /reset-password     Valida el codigo y actualiza la contrasena
 */
class PasswordController extends BaseController
{
    /**
     * Muestra el formulario para solicitar la recuperacion.
     */
    public function olvide()
    {
        return view('password/olvide_password');
    }

    /**
     * Procesa la solicitud: genera token + codigo y envia el correo.
     */
    public function enviarEnlace()
    {
        $email = trim($this->request->getPost('email'));

        if (empty($email)) {
            return redirect()->back()->with('error', 'Por favor ingresa tu correo electronico.');
        }

        $personaModel = new PersonaModel();
        $usuario      = $personaModel->where('Correo_usu', $email)
                                     ->where('estado', 1)
                                     ->first();

        // Mensaje neutro para no revelar si el correo existe
        $mensajeNeutro = 'Si el correo esta registrado, recibiras un mensaje con las instrucciones.';

        if (! $usuario) {
            return redirect()->to('reset-password')->with('mensaje', $mensajeNeutro);
        }

        // Genera token (enlace) y codigo de 6 digitos (ingreso manual)
        $token  = bin2hex(random_bytes(32));
        $codigo = str_pad((string) random_int(0, 999999), 6, '0', STR_PAD_LEFT);

        $resetModel = new PasswordResetModel();

        // Invalida tokens previos del mismo correo
        $resetModel->where('correo', $email)->set(['usado' => 1])->update();

        $resetModel->insert([
            'correo'     => $email,
            'token'      => hash('sha256', $token),
            'codigo'     => $codigo,
            'expira'     => date('Y-m-d H:i:s', strtotime('+15 minutes')),
            'usado'      => 0,
            'created_at' => date('Y-m-d H:i:s'),
        ]);

        $enlace = base_url('reset-password?token=' . $token);
        $nombre = trim(($usuario['Nom1_usu'] ?? '') . ' ' . ($usuario['Ape1_usu'] ?? ''));
        $cuerpo = $this->plantillaCorreo($nombre, $codigo, $enlace);

        $emailService = \Config\Services::email();
        $emailService->setTo($email);
        $emailService->setSubject('Recuperacion de contrasena - SISPE');
        $emailService->setMessage($cuerpo);
        $emailService->setMailType('html');

        if (! $emailService->send(false)) {
            return redirect()->back()->with(
                'error',
                'No se pudo enviar el correo. Revisa la configuracion SMTP en el archivo .env.'
            );
        }

        return redirect()->to('reset-password')->with(
            'mensaje',
            'Te enviamos un correo con el codigo de recuperacion. Revisa tu bandeja de entrada.'
        );
    }

    /**
     * Muestra el formulario para ingresar el codigo y la nueva contrasena.
     */
    public function reset()
    {
        // Si llega por enlace, precargamos el token en el formulario
        $token = $this->request->getGet('token');

        return view('password/reset_password', ['token' => $token]);
    }

    /**
     * Valida el codigo/token y actualiza la contrasena.
     */
    public function actualizar()
    {
        $token           = trim($this->request->getPost('token'));
        $email           = trim($this->request->getPost('email'));
        $codigo          = trim($this->request->getPost('codigo'));
        $password        = trim($this->request->getPost('password'));
        $passwordConfirm = trim($this->request->getPost('password_confirm'));

        if (empty($password) || strlen($password) < 4) {
            return redirect()->back()->withInput()
                ->with('error', 'La contrasena debe tener al menos 4 caracteres.');
        }

        if ($password !== $passwordConfirm) {
            return redirect()->back()->withInput()
                ->with('error', 'Las contrasenas no coinciden.');
        }

        if (empty($token) && (empty($email) || empty($codigo))) {
            return redirect()->back()->withInput()
                ->with('error', 'Debes ingresar el codigo enviado a tu correo.');
        }

        $resetModel = new PasswordResetModel();
        $builder    = $resetModel->where('usado', 0)
                                 ->where('expira >=', date('Y-m-d H:i:s'));

        if (! empty($token)) {
            $builder->where('token', hash('sha256', $token));
        } else {
            $builder->where('correo', $email)->where('codigo', $codigo);
        }

        $registro = $builder->orderBy('id', 'DESC')->first();

        if (! $registro) {
            return redirect()->back()->withInput()
                ->with('error', 'El codigo es invalido o ya expiro. Solicita uno nuevo.');
        }

        $personaModel = new PersonaModel();
        $usuario      = $personaModel->where('Correo_usu', $registro['correo'])->first();

        if (! $usuario) {
            return redirect()->back()->with('error', 'El usuario asociado no existe.');
        }

        $personaModel->set('Password', password_hash($password, PASSWORD_DEFAULT))
                     ->where('id_usuario', $usuario['id_usuario'])
                     ->where('pkfk_Tipo_doc', $usuario['pkfk_Tipo_doc'])
                     ->update();

        $resetModel->update($registro['id'], ['usado' => 1]);

        return redirect()->to('/')->with(
            'mensaje',
            'Tu contrasena se actualizo correctamente. Ya puedes iniciar sesion.'
        );
    }

    /**
     * Plantilla HTML del correo de recuperacion.
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
