SELECT usuario.id_usuario, nombre_usu, apellido_usu, desc_telefono, n_telefono
FROM usuario
JOIN usuario_telefonos ON usuario.id_usuario = usuario_telefonos.id_usuario and  usuario.cod_tdoc = usuario_telefonos.cod_tdoc 
JOIN telefonos ON usuario_telefonos.cod_telefono = telefonos.cod_telefono;