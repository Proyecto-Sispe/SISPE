<?php

namespace App\Controllers;

use App\Models\AdminPersonaModel;
use CodeIgniter\Database\Config;

class AdminPersonaController extends BaseController
{
    protected $personaModel;

    public function __construct()
    {
        $this->personaModel = new AdminPersonaModel();
    }

    // 1. LISTAR Y FILTRAR USUARIOS
    public function index()
    {
        // Seguridad: Si no está logueado, lo saca patitas a la calle
        if (!session('logueado')) {
            return redirect()->to('/');
        }

        // Capturamos lo que venga por GET desde los filtros de la vista
        $doc   = $this->request->getGet('doc');
        $rol   = $this->request->getGet('rol');
        $texto = $this->request->getGet('buscar');

        // Consultamos con filtros pasados
        $data['usuarios']   = $this->personaModel->obtenerUsuarios($doc, $rol, $texto);
        
        // Mantener los valores en los campos de filtro después de buscar
        $data['filtro_doc']  = $doc;
        $data['filtro_rol']  = $rol;
        $data['filtro_text'] = $texto;

        return view('admin/personas_listado', $data);
    }

    // 2. MOSTRAR FORMULARIO "AGREGAR PERSONA"
    public function crear()
    {
        if (!session('logueado')) return redirect()->to('/');
        return view('admin/personas_agregar');
    }

    // 3. PROCESAR GUARDADO DE NUEVA PERSONA
    public function guardar()
    {
        $db = Config::connect();
        $id_usuario = $this->request->getPost('id_usuario');
        $tipo_doc   = $this->request->getPost('pkfk_Tipo_doc');
        $id_rol     = $this->request->getPost('id_rol');

        $datos = [
            'id_usuario'    => $id_usuario,
            'pkfk_Tipo_doc' => $tipo_doc,
            'Nom1_usu'      => $this->request->getPost('Nom1_usu'),
            'Nom2_usu'      => $this->request->getPost('Nom2_usu') ?: null,
            'Ape1_usu'      => $this->request->getPost('Ape1_usu'),
            'Ape2_usu'      => $this->request->getPost('Ape2_usu') ?: null,
            'Telefono'      => $this->request->getPost('Telefono') ?: 0,
            'Correo_usu'    => $this->request->getPost('Correo_usu'),
            'Password'      => password_hash($this->request->getPost('Password'), PASSWORD_DEFAULT),
            'estado'        => 1
        ];

        $this->personaModel->insert($datos);

        // Guardamos la relación con el rol elegido en el select
        $db->table('Persona_has_Rol')->insert([
            'pkfk_Tipo_doc'   => $tipo_doc,
            'pkfk_id_usuario' => $id_usuario,
            'pkfk_idRol'      => $id_rol
        ]);

        return redirect()->to('personas')->with('success', 'Persona agregada con éxito.');
    }

    // 4. MOSTRAR FORMULARIO "EDITAR PERSONA"
    public function editar($id, $tipo_doc)
    {
        if (!session('logueado')) return redirect()->to('/');

        // Buscamos los datos actuales haciendo join para saber qué rol tiene
        $db = Config::connect();
        $builder = $db->table('Persona p');
        $builder->select('p.*, phr.pkfk_idRol as id_rol');
        $builder->join('Persona_has_Rol phr', 'p.id_usuario = phr.pkfk_id_usuario AND p.pkfk_Tipo_doc = phr.pkfk_Tipo_doc');
        $builder->where('p.id_usuario', $id);
        $builder->where('p.pkfk_Tipo_doc', $tipo_doc);
        
        $data['persona'] = $builder->get()->getRowArray();

        if (!$data['persona']) {
            return redirect()->to('personas')->with('error', 'Usuario no encontrado.');
        }

        return view('admin/personas_editar', $data);
    }

    // 5. PROCESAR ACTUALIZACIÓN DE CAMBIOS
    public function actualizar()
    {
        $db = Config::connect();
        
        // Llaves compuestas originales ocultas en el form para saber a quién actualizar
        $id_original   = $this->request->getPost('id_original');
        $doc_original  = $this->request->getPost('doc_original');

        $id_rol_nuevo  = $this->request->getPost('id_rol');
        $password_new  = $this->request->getPost('Password');

        $datosActualizar = [
            'Nom1_usu'   => $this->request->getPost('Nom1_usu'),
            'Nom2_usu'   => $this->request->getPost('Nom2_usu') ?: null,
            'Ape1_usu'   => $this->request->getPost('Ape1_usu'),
            'Ape2_usu'   => $this->request->getPost('Ape2_usu') ?: null,
            'Telefono'   => $this->request->getPost('Telefono') ?: 0,
            'Correo_usu' => $this->request->getPost('Correo_usu')
        ];

        // Si el admin escribió algo en el campo contraseña, la encriptamos y actualizamos
        if (!empty($password_new)) {
            $datosActualizar['Password'] = password_hash($password_new, PASSWORD_DEFAULT);
        }

        // Ejecutamos update usando la llave compuesta
        $this->personaModel->where('id_usuario', $id_original)
                           ->where('pkfk_Tipo_doc', $doc_original)
                           ->set($datosActualizar)
                           ->update();

        // Actualizamos su rol en la tabla intermedia
        $db->table('Persona_has_Rol')
           ->where('pkfk_id_usuario', $id_original)
           ->where('pkfk_Tipo_doc', $doc_original)
           ->update(['pkfk_idRol' => $id_rol_nuevo]);

        return redirect()->to('personas')->with('success', 'Datos actualizados correctamente.');
    }

    // 6. ELIMINAR (BORRADO LÓGICO)
    public function eliminar($id, $tipo_doc)
    {
        // En vez de hacer DELETE (que rompería FKs), cambiamos estado a 0 (Inactivo)
        $this->personaModel->where('id_usuario', $id)
                           ->where('pkfk_Tipo_doc', $tipo_doc)
                           ->set(['estado' => 0])
                           ->update();

        return redirect()->to('personas')->with('success', 'Usuario dado de baja del panel.');
    }
}
