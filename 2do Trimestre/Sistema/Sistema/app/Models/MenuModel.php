<?php

namespace App\Models;

use CodeIgniter\Model;

class MenuModel extends Model
{
    protected $table            = 'Menu';
    protected $primaryKey       = 'id_menu';
    protected $useAutoIncrement = false;
    protected $returnType       = 'array';
    protected $allowedFields    = ['Productos', 'Precio', 'descripcion', 'pkfk_id_categoria'];

    /**
     * Devuelve los productos junto a su categoría.
     * @return array
     */
    public function obtenerProductosConCategoria()
    {
        $builder = $this->select("
            Menu.id_menu,
            Menu.Productos,
            Menu.Precio,
            Menu.descripcion,
            Categoria.nom_categoria
        ")
        ->join('Categoria', 'Menu.pkfk_id_categoria = Categoria.id_categoria', 'left');

        return $builder->orderBy('Categoria.nom_categoria', 'ASC')->findAll();
    }
}
