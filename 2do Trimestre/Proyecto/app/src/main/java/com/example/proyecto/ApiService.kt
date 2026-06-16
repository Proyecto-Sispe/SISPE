package com.example.proyecto


import retrofit2.Response
import retrofit2.http.GET


interface ApiService {


    @GET("api/menu")

    suspend fun obtenerMenu():
            Response<List<Menu>>


}