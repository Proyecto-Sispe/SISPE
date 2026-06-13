<?php

namespace App\Models;

use CodeIgniter\Model;

class PersonaModel extends Model
{
    protected $table            = 'Persona';
    protected $primaryKey       = 'id_usuario'; 
    protected $useAutoIncrement = false;       
    protected $returnType       = 'array';
    protected $allowedFields    = [
        'id_usuario', 
        'pkfk_Tipo_doc', 
        'Nom1_usu', 
        'Nom2_usu', 
        'Ape1_usu', 
        'Ape2_usu', 
        'Telefono', 
        'Correo_usu', 
        'Password', 
        'estado'
    ];
    
    protected $useTimestamps = false;
}
