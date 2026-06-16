package com.example.proyecto


import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import kotlinx.coroutines.launch



class CrudActivity : AppCompatActivity(){


    private lateinit var repo: ProyectoRepository

    private lateinit var recycler: RecyclerView



    override fun onCreate(savedInstanceState: Bundle?) {


        super.onCreate(savedInstanceState)


        setContentView(R.layout.activity_crud)



        repo = ProyectoRepository(
            RetrofitClient.instance
        )



        recycler = findViewById(
            R.id.rvProductos
        )



        recycler.layoutManager =
            LinearLayoutManager(this)



        cargarMenu()



    }



    private fun cargarMenu(){


        lifecycleScope.launch{


            val menu =
                repo.listarMenu()



            recycler.adapter =
                MenuAdapter(menu ?: emptyList())


        }


    }


}