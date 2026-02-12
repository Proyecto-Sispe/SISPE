<?php

class database{

	private static $dbHost = "localhost";
    private static $dbName = "telefonos";
    private static $dbUsername = "root";
    private static $dbUserpassword = "";
    
    
    public static function conectar(){
        
        try {

		$con = new PDO("mysql:host=".self::$dbHost.";dbname=".self::$dbName,self::$dbUsername,self::$dbUserpassword);
        $con->setAttribute(PDO::ATTR_ERRMODE,PDO::ERRMODE_EXCEPTION);
         return $con;
        } catch (Exception $e) {
            die($e->getMessage());
        }
    }
    
}
?>