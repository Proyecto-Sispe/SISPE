<?php 
	class user
	{
		private $t_teldo;
		
		public function __CONSTRUCT()
		{
			try{
				$this->pdo = database::conectar();
			}
			catch(Exception $ex){
				die($e->getMessage());
			}
		}

		public function Insert_user($id, $nom, $ape, $dir)
		{
			$sql = "INSERT INTO user (Id_user, nombre_user, apellido_user, Direccion_user) VALUES ('$id', '$nom', '$ape', '$dir');";

			$this->pdo->query($sql);

			// consulta que trea los tipos de telefono existentes para hacer la condicion de los chequeados
 			$stm1 = $this->pdo->prepare("SELECT tipo_tel from tipo_telefono");
			$stm1->execute();

			//Realiza el ciclo de todos los objetos o lines que se encuentra en la consulta
			foreach($stm1->fetchAll(PDO::FETCH_OBJ) as $r)
			{
				// variable que almacena lo que encunetra en el campo tipo telefonos
				$t_tel= $r->tipo_tel;

				// Comporbar si el checbox esta selecionado (true) que tiene la variable seleccionada anteriormente - tipo telefonos.
				if (isset($_POST[$t_tel])) {

				// Concatenar lo obtenido en los checkbox del tipo_telefono.
					$val_tel="num".$t_tel;
				//Busca lo que se almaceno en el campo numcell o numfijo
					$num_tel=$_REQUEST[$val_tel];
					$sql1 = "INSERT INTO telefono_has_user (tipotel, Id_usu, num_tel) VALUES ('$t_tel', '$id', '$num_tel')";
					$this->pdo->query($sql1);
				}
			}
			print "<script>alert(\"Registro agregado exitosamente. \");window.location='view_user.php';</script>";
		}
}
?>