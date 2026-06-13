<?php

namespace App\Models;

use CodeIgniter\Model;

class AdminPersonaModel extends Model
{
    protected $table            = 'Persona';
    protected $primaryKey       = 'id_usuario';
    protected $useAutoIncrement = false;
    protected $returnType       = 'array';
    protected $allowedFields    = [
        'id_usuario', 'pkfk_Tipo_doc', 'Nom1_usu', 'Nom2_usu', 
        'Ape1_usu', 'Ape2_usu', 'Telefono', 'Correo_usu', 'Password', 'estado'
    ];

    // Función pro para obtener listado con filtros dinámicos
    public function obtenerUsuarios($buscarDoc = null, $buscarRol = null, $buscarTexto = null)
    {
        $builder = $this->db->table('Persona p');
        $builder->select('p.*, td.tipo_doc as nombre_documento, r.Nom_rol, r.idRol');
        $builder->join('Tipo_doc td', 'p.pkfk_Tipo_doc = td.id_doc');
        $builder->join('Persona_has_Rol phr', 'p.id_usuario = phr.pkfk_id_usuario AND p.pkfk_Tipo_doc = phr.pkfk_Tipo_doc');
        $builder->join('Rol r', 'phr.pkfk_idRol = r.idRol');
        
        // Solo traer usuarios activos (estado = 1)
        $builder->where('p.estado', 1);

        // Filtro por Tipo de Documento si se selecciona uno
        if (!empty($buscarDoc)) {
            $builder->where('p.pkfk_Tipo_doc', $buscarDoc);
        }

        // Filtro por Rol si se selecciona uno
        if (!empty($buscarRol)) {
            $builder->where('r.idRol', $buscarRol);
        }

        // Filtro de búsqueda por texto libre (Busca en ID, Nombre o Apellido)
        if (!empty($buscarTexto)) {
            $builder->groupStart()
                    ->like('p.id_usuario', $buscarTexto)
                    ->orLike('p.Nom1_usu', $buscarTexto)
                    ->orLike('p.Ape1_usu', $buscarTexto)
                    ->groupEnd();
        }

        return $builder->get()->getResultArray();
    }
}
