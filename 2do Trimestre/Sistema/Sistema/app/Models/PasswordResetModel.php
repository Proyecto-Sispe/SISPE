<?php

namespace App\Models;

use CodeIgniter\Model;

class PasswordResetModel extends Model
{
    protected $table         = 'password_resets';
    protected $primaryKey    = 'id';
    protected $returnType    = 'array';
    protected $allowedFields = ['correo', 'token', 'codigo', 'expira', 'usado', 'created_at'];

    protected $useTimestamps = false;
}
