<?php

namespace App\Models;

use CodeIgniter\Model;

class MesaModel extends Model
{
    protected $table            = 'Mesa';
    protected $primaryKey       = 'id_Mesa';
    protected $useAutoIncrement = false; // Insertamos los números manualmente (1, 2, 3...)
    protected $returnType       = 'array';
    protected $allowedFields    = ['id_Mesa', 'Capacidad', 'Ubicacion', 'Estado'];
}