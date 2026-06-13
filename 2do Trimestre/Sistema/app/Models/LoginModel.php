<?php

namespace App\Models;

use CodeIgniter\Model;

class LoginModel extends Model
{
    protected $table            = 'Persona';
    protected $primaryKey       = 'id_usuario';
    protected $returnType       = 'array';
    protected $allowedFields    = ['Correo_usu', 'Password', 'estado'];
}
