<?php

namespace App\Controllers;

use App\Models\MenuModel;
use CodeIgniter\Database\Config;

class MenuController extends BaseController
{
    // 1. Panel de Administración (Listar y Formulario)
    public function index()
    {
        if (!session('logueado')) return redirect()->to('/');
        
        $menuModel = new MenuModel();
        $db = Config::connect();

        // Traemos los productos con su join de categoría
        $datos['productos'] = $menuModel->obtenerProductosConCategoria();
        
        // Traemos las categorías para cargar el <select> del formulario
        $datos['categorias'] = $db->table('Categoria')->get()->getResultArray();

        return view('menu/crud_menu', $datos);
    }

    // 2. Insertar nuevo producto al menú (ID manual porque useAutoIncrement = false)
    public function guardar()
    {
        if (!session('logueado')) return redirect()->to('/');

        $menuModel = new MenuModel();
        
        $nuevoPlato = [
            'id_menu'            => $this->request->getPost('id_menu'), // ID Manual requerido
            'Productos'          => $this->request->getPost('Productos'),
            'Precio'             => $this->request->getPost('Precio'),
            'descripcion'        => $this->request->getPost('descripcion'),
            'pkfk_id_categoria'  => $this->request->getPost('pkfk_id_categoria')
        ];

        $menuModel->insert($nuevoPlato);

        return redirect()->to('/gestion-menu')->with('mensaje', 'Producto agregado con éxito.');
    }

    // 3. Eliminar producto del menú
    public function eliminar($id)
    {
        if (!session('logueado')) return redirect()->to('/');

        $menuModel = new MenuModel();
        $menuModel->delete($id);

        return redirect()->to('/gestion-menu')->with('mensaje', 'Producto eliminado.');
    }

    // 4. Vista del Cliente (El Menú Digital con tus tarjetas Coral)
    public function digital()
    {
        $menuModel = new MenuModel();
        $productos = $menuModel->obtenerProductosConCategoria();
        
        // Agrupamos los platos por el nombre de su categoría en la BD
        $menuCategorizado = [];
        foreach ($productos as $prod) {
            $cat = !empty($prod['nom_categoria']) ? $prod['nom_categoria'] : 'Especialidades';
            $menuCategorizado[$cat][] = $prod;
        }

        return view('menu/menu_digital', ['menuCategorizado' => $menuCategorizado]);
    }
    // ... Todo el código anterior del controlador se mantiene igual ...

    // Método nuevo para añadir categorías desde el formulario
    public function guardarCategoria()
    {
        if (!session('logueado')) return redirect()->to('/');

        $db = \Config\Database::connect();
        
        $nuevaCategoria = [
            'id_categoria'  => $this->request->getPost('id_categoria'), // Si es manual, o lo dejas vacío si es autoincrementable
            'nom_categoria' => $this->request->getPost('nom_categoria')
        ];

        $db->table('Categoria')->insert($nuevaCategoria);

        return redirect()->to('/gestion-menu')->with('mensaje', 'Categoría creada con éxito.');
    }
}

