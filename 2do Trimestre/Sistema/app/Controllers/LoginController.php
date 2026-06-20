<?php

namespace App\Controllers;

use CodeIgniter\Database\Config;

class LoginController extends BaseController
{
    public function index()
    {
        return view('login'); 
    }

    public function login()
    {
        $session = session();
        
        // Captura los datos enviados desde el formulario por su atributo 'name'
        $email    = trim($this->request->getPost('email'));
        $password = trim($this->request->getPost('password'));

        if (empty($email) || empty($password)) {
            return redirect()->to('login')->with('error', 'Por favor complete todos los campos.');
        }

        $db = Config::connect();

        // Consulta limpia basada 100% en tu script: Busca en Persona y trae el nombre del Rol
        $sql = "SELECT p.*, r.Nom_rol 
                FROM Persona p
                INNER JOIN Persona_has_Rol phr ON p.id_usuario = phr.pkfk_id_usuario AND p.pkfk_Tipo_doc = phr.pkfk_Tipo_doc
                INNER JOIN Rol r ON phr.pkfk_idRol = r.idRol
                WHERE p.Correo_usu = ? AND p.estado = 1";

        $usuario = $db->query($sql, [$email])->getRowArray();

        if ($usuario) {
            // Comprobación compatible: acepta la contraseña '1234' en texto plano de tus INSERTS
            // y también acepta las contraseñas seguras (hashes) de los usuarios nuevos.
            if (password_verify($password, $usuario['Password']) || ($password === $usuario['Password'])) {
                
                // Guardamos los datos reales en la sesión para los filtros del menú
                $session->set([
                    'id_usuario' => $usuario['id_usuario'],
                    'nombre'     => $usuario['Nom1_usu'] . ' ' . $usuario['Ape1_usu'],
                    'rol'        => $usuario['Nom_rol'], // Guardará 'Administrador', 'Mesero', etc.
                    'logueado'   => true
                ]);

                return redirect()->to('/dashboard');
            } else {
                return redirect()->to('login')->with('error', 'Contraseña incorrecta.');
            }
        } else {
            return redirect()->to('login')->with('error', 'El usuario no existe o los datos son incorrectos.');
        }
    }

    public function dashboard()
    {
        if (!session('logueado')) {
            return redirect()->to('login');
        }
        return view('dashboard');
    }

    public function logout()
    {
        session()->destroy();
        return redirect()->to('/');
    }
}

