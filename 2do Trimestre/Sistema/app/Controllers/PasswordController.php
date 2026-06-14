<?php

namespace App\Controllers;

use CodeIgniter\Database\Config;
use Config\Services;

class PasswordController extends BaseController
{
    // Muestra el formulario para solicitar el enlace de recuperacion.
    public function olvide()
    {
        return view('olvide_password');
    }

    // Genera token + codigo, los guarda en password_resets e intenta enviarlos
    // por correo. Si el correo no esta configurado, muestra el enlace en pantalla.
    public function enviarEnlace()
    {
        $correo = trim((string) $this->request->getPost('email'));

        if (empty($correo)) {
            return redirect()->back()->with('error', 'Ingresa tu correo electronico.');
        }

        $db = Config::connect();

        $usuario = $db->query(
            "SELECT id_usuario, Correo_usu, Nom1_usu FROM Persona WHERE Correo_usu = ? AND estado = 1",
            [$correo]
        )->getRowArray();

        // Por seguridad, no revelamos si el correo existe o no.
        if (! $usuario) {
            return redirect()->back()->with('mensaje', 'Si el correo esta registrado, recibiras instrucciones para restablecer tu contrasena.');
        }

        $tokenPlano = bin2hex(random_bytes(32));        // se envia en el enlace
        $tokenHash  = hash('sha256', $tokenPlano);      // se guarda en la BD
        $codigo     = str_pad((string) random_int(0, 999999), 6, '0', STR_PAD_LEFT);
        $ahora      = date('Y-m-d H:i:s');
        $expira     = date('Y-m-d H:i:s', time() + 15 * 60); // 15 minutos

        $db->query("UPDATE password_resets SET usado = 1 WHERE correo = ? AND usado = 0", [$correo]);

        $db->query(
            "INSERT INTO password_resets (correo, token, codigo, expira, usado, created_at)
             VALUES (?, ?, ?, ?, 0, ?)",
            [$correo, $tokenHash, $codigo, $expira, $ahora]
        );

        $enlace = base_url('reset-password?token=' . $tokenPlano);

        $enviado = $this->enviarCorreo($correo, $usuario['Nom1_usu'] ?? '', $enlace, $codigo);

        if ($enviado) {
            return redirect()->back()->with('mensaje', 'Te enviamos un correo con el enlace y el codigo para restablecer tu contrasena. Revisa tu bandeja de entrada y la carpeta de spam.');
        }

        // Respaldo en pantalla (cuando el SMTP no esta configurado en localhost)
        return redirect()->to('reset-password?token=' . $tokenPlano)
            ->with('mensaje', 'No se pudo enviar el correo (SMTP no configurado). Como respaldo, te llevamos directamente al formulario. Tu codigo de verificacion es: ' . $codigo);
    }

    // Muestra el formulario para escribir la nueva contrasena.
    public function reset()
    {
        $token = (string) $this->request->getGet('token');

        if (empty($token)) {
            return redirect()->to('olvide-password')->with('error', 'Enlace invalido. Solicita uno nuevo.');
        }

        $registro = $this->buscarSolicitudValida($token);

        if (! $registro) {
            return redirect()->to('olvide-password')->with('error', 'El enlace es invalido o ha expirado. Solicita uno nuevo.');
        }

        return view('reset_password', ['token' => $token]);
    }

    // Procesa el cambio de contrasena.
    public function actualizar()
    {
        $token     = (string) $this->request->getPost('token');
        $password  = (string) $this->request->getPost('password');
        $password2 = (string) $this->request->getPost('password_confirm');

        if (empty($token)) {
            return redirect()->to('olvide-password')->with('error', 'Enlace invalido. Solicita uno nuevo.');
        }

        if (empty($password) || strlen($password) < 4) {
            return redirect()->back()->with('error', 'La contrasena debe tener al menos 4 caracteres.');
        }

        if ($password !== $password2) {
            return redirect()->back()->with('error', 'Las contrasenas no coinciden.');
        }

        $registro = $this->buscarSolicitudValida($token);

        if (! $registro) {
            return redirect()->to('olvide-password')->with('error', 'El enlace es invalido o ha expirado. Solicita uno nuevo.');
        }

        $db = Config::connect();

        // Actualiza la contrasena del usuario (siempre encriptada)
        $db->query(
            "UPDATE Persona SET Password = ? WHERE Correo_usu = ?",
            [password_hash($password, PASSWORD_DEFAULT), $registro['correo']]
        );

        $db->query("UPDATE password_resets SET usado = 1 WHERE id = ?", [$registro['id']]);

        return redirect()->to('/')->with('mensaje', 'Tu contrasena fue actualizada correctamente. Ya puedes iniciar sesion.');
    }

    // Busca una solicitud valida (no usada y no expirada) a partir del token plano.
    private function buscarSolicitudValida(string $tokenPlano): ?array
    {
        $db        = Config::connect();
        $tokenHash = hash('sha256', $tokenPlano);

        $registro = $db->query(
            "SELECT * FROM password_resets WHERE token = ? AND usado = 0 AND expira >= ? LIMIT 1",
            [$tokenHash, date('Y-m-d H:i:s')]
        )->getRowArray();

        return $registro ?: null;
    }

    // Envia el correo de recuperacion. Devuelve false si el SMTP no esta configurado.
    private function enviarCorreo(string $correo, string $nombre, string $enlace, string $codigo): bool
    {
        if (empty(env('email.SMTPUser')) || empty(env('email.SMTPPass'))) {
            return false;
        }

        try {
            $email = Services::email();

            $mensaje = '<div style="font-family:Arial,sans-serif;max-width:520px;margin:auto">'
                . '<h2>Recuperacion de contrasena - SISPE</h2>'
                . '<p>Hola ' . esc($nombre) . ',</p>'
                . '<p>Recibimos una solicitud para restablecer tu contrasena. Haz clic en el siguiente boton:</p>'
                . '<p><a href="' . esc($enlace, 'attr') . '" style="background:#2ec4b6;color:#fff;padding:12px 20px;border-radius:8px;text-decoration:none;display:inline-block">Restablecer contrasena</a></p>'
                . '<p>O usa este codigo de verificacion: <b style="font-size:18px">' . esc($codigo) . '</b></p>'
                . '<p>Este enlace expira en 15 minutos. Si no solicitaste esto, ignora este correo.</p>'
                . '</div>';

            $email->setTo($correo);
            $email->setSubject('Recuperacion de contrasena - SISPE');
            $email->setMessage($mensaje);

            return (bool) $email->send();
        } catch (\Throwable $e) {
            log_message('error', 'Error enviando correo de recuperacion: ' . $e->getMessage());
            return false;
        }
    }
}