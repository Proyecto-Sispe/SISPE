<?php

namespace App\Controllers;

use CodeIgniter\RESTful\ResourceController;
use App\Models\ProductoModel;


class ProductoController extends ResourceController
{

public function index()
{

$model = new ProductoModel();

return $this->respond(
$model->findAll()
);

}


public function create()
{

$model = new ProductoModel();

$json = $this->request->getJSON();


$data=[

'nombre'=>$json->nombre,

'descripcion'=>$json->descripcion,

'precio'=>$json->precio

];


$model->insert($data);


return $this->respond([
"mensaje"=>"Producto guardado"
]);

}


public function delete($id=null)
{

$model = new ProductoModel();

$model->delete($id);


return $this->respond([
"mensaje"=>"Producto eliminado"
]);

}


}