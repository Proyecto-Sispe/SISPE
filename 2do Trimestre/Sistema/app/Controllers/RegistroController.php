<?php

namespace App\Controllers;

use CodeIgniter\Database\Config;

class RegistroController extends BaseController
{
    public function registrar()
    {
        return view('registro'); 
    }

    public function guardar()
    {
        $db = Config::connect();

        // Captura blindada para evitar el error 'id_usuario cannot be null'
        // Busca el atributo name="id" o name="id_usuario" del formulario
        $id_usuario = $this->request->getPost('id') ?: $this->request->getPost('id_usuario');
        $tipo_doc   = $this->request->getPost('doc') ?: $this->request->getPost('pkfk_Tipo_doc');

        if (empty($id_usuario) || empty($tipo_doc)) {
            return redirect()->back()->with('error', 'El número de identificación y tipo de documento son obligatorios.');
        }

        // Insertar los datos directamente en la tabla Persona
        $sqlPersona = "INSERT INTO Persona (id_usuario, pkfk_Tipo_doc, Nom1_usu, Nom2_usu, Ape1_usu, Ape2_usu, Telefono, Correo_usu, Password, estado) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)";
        
        $db->query($sqlPersona, [
            $id_usuario,
            $tipo_doc,
            $this->request->getPost('nombre1'),
            $this->request->getPost('nombre2') ?: null,
            $this->request->getPost('apellido1'),
            $this->request->getPost('apellido2') ?: null,
            $this->request->getPost('telefono'),
            trim($this->request->getPost('email')),
            password_hash(trim($this->request->getPost('password')), PASSWORD_DEFAULT) // Encriptación correcta
        ]);

        // Asignación automática: Rol de Cliente (ID 4) de tus INSERTS base
        $idRolPredeterminado = 4; 
        
        $sqlRol = "INSERT INTO Persona_has_Rol (pkfk_Tipo_doc, pkfk_id_usuario, pkfk_idRol) VALUES (?, ?, ?)";
        $db->query($sqlRol, [$tipo_doc, $id_usuario, $idRolPredeterminado]);

        return redirect()->to('/')->with('mensaje', '¡Registro exitoso! Ya puedes iniciar sesión.');
    }
}


