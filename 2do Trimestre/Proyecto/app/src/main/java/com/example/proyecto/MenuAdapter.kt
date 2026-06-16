package com.example.proyecto


import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView



class MenuAdapter(
    private val lista: List<Menu>
) : RecyclerView.Adapter<MenuAdapter.ViewHolder>() {



    class ViewHolder(view: View) : RecyclerView.ViewHolder(view){


        val nombre: TextView =
            view.findViewById(R.id.tvNombre)


        val descripcion: TextView =
            view.findViewById(R.id.tvDescripcion)


        val precio: TextView =
            view.findViewById(R.id.tvPrecio)


    }



    override fun onCreateViewHolder(
        parent: ViewGroup,
        viewType: Int
    ): ViewHolder {


        val vista = LayoutInflater.from(parent.context)
            .inflate(
                R.layout.item_menu,
                parent,
                false
            )


        return ViewHolder(vista)

    }



    override fun onBindViewHolder(
        holder: ViewHolder,
        position: Int
    ) {


        val menu = lista[position]


        holder.nombre.text =
            menu.Productos


        holder.descripcion.text =
            menu.descripcion


        holder.precio.text =
            "$ ${menu.Precio.toInt()}"



    }



    override fun getItemCount(): Int {


        return lista.size


    }


}