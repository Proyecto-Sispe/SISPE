<?php
require_once 'model_user.php';
require_once '../BD/conexion.php';

$db = database::conectar();

// INICIO DE VALIDACION Y SELECCION DE CASOS A REALIZAR INSERT - UPDATE - DELETE - SELECT
if(isset($_REQUEST['action']))
{ 	switch ($_REQUEST['action']) 
	{ 	

// CASO PARA METODO REGISTRAR		
		case 'registrar':

			$insert=new user();
  			$insert->Insert_user($_POST["id_usu"], $_POST["nom_usu"], $_POST["ape_usu"], $_POST["dir_usu"]);
         break;
	}
}
// FIN SECCION DE CASOS

?>
<!DOCTYPE html>
<html>
<head>
	<title>EJEMPLO INSTRUCTOR - LEONARDO</title>
	<link rel="stylesheet" type="text/css" href="../css/style_crud.css">
</head>
<body>

<a href="?action=ver&m=1">NEW USER</a><br><br>

<!-- Validacion para mostrar formulario de nuevo registro -->
	<?php if( !empty($_GET['m']) and !empty($_GET['action'])  )

{?>

<div>
<!-- Formulario nuevo registro -->
	<form action='#' method="POST">
		<h2>NEW USER</h2>

		<label>user id</label>   
		<input type="text" name="id_usu" placeholder="user id" required>
		
		<label>user name</label>   
		<input type="text" name="nom_usu" placeholder="user name" required>
		
		<label>user Surname</label>   
		<input type="text" name="ape_usu" placeholder="user Surname" required>
		
		<label>user Adrres</label>   
		<input type="text" name="dir_usu" placeholder="user Adrres" required>

<!--Ciclo que muestra los tipos de telefonos existentes y campo para agregar el numero de telefono-->
      <?php
      foreach ($db->query('SELECT * FROM tipo_telefono') as $row) { ?>

        <input type="checkbox" name="<?php echo $row['tipo_tel']; ?>">
        <?php echo $row['tipo_tel']; ?>
        <input type="text" name="num<?php echo $row['tipo_tel']; ?>"><br><br>

      <?php } ?>



			<br><input class="submit-button" type="submit" value="Guardar" onclick = "this.form.action = '?action=registrar';"/>
<?php }  ?> <!-- FIN - Formulario nuevo registro -->		
	</form>
</div>

<?php  
$sql1= "
SELECT Id_user, nombre_user, apellido_user, Direccion_user, tipotel, num_tel
FROM user
JOIN telefono_has_user ON Id_user = Id_usu  
ORDER BY nombre_user ASC";
$query = $db->query($sql1);

if($query->rowCount()>0):?>
<br><h1>Users Records</h1><br>

<?php while ($row=$query->fetch(PDO::FETCH_ASSOC)): 

	echo $row['Id_user']."<br>";
	echo $row['nombre_user']." ".$row['apellido_user']."<br>";
	echo $row['Direccion_user']."<br>";
	echo $row['tipotel'].": ".$row['num_tel']."<p>";
endwhile;?>



<?php else:?>
	<h4 class="alert alert-danger">Mr. User DO NOT find Registration</h4>
<?php endif;?>

</body>
</html>


