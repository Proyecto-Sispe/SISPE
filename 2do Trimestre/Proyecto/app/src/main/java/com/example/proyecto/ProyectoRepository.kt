package com.example.proyecto


class ProyectoRepository(
    private val api: ApiService
) {


    suspend fun listarMenu():

            List<Menu>? {


        return try {


            val respuesta =
                api.obtenerMenu()


            if(respuesta.isSuccessful){


                respuesta.body()


            }else{


                null


            }


        }catch(e:Exception){


            null


        }


    }


}