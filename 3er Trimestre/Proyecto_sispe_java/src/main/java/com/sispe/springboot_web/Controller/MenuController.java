package com.sispe.springboot_web.Controller;

import com.sispe.springboot_web.Model.Menu;
import com.sispe.springboot_web.Service.MenuService;
import com.sispe.springboot_web.Repository.CategoriaRepository;
import com.sispe.springboot_web.Repository.AdicionRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.UUID;

@Controller
@RequiredArgsConstructor
public class MenuController {
    private final MenuService service;
    private final CategoriaRepository categorias;
    private final AdicionRepository adiciones;
    private static final Path CARPETA_FOTOS = Path.of("uploads", "menu");

    @GetMapping("/menu")
    public String index(Model model) {
        model.addAttribute("productos", service.listar());
        model.addAttribute("categorias", categorias.findAll());
        model.addAttribute("menu", new Menu());
        return "menu/index";
    }

    @GetMapping("/menu/digital")
    public String digital(Model model) {
        model.addAttribute("productos", service.listar());
        model.addAttribute("adiciones", adiciones.findAll());
        return "menu/digital";
    }

    @PostMapping("/menu/guardar")
    public String guardar(@ModelAttribute Menu menu,
                           @RequestParam(value = "fotoArchivo", required = false) MultipartFile fotoArchivo,
                           RedirectAttributes attributes) {
        if (menu.getCategoria() == null || menu.getCategoria().getId() == null || !categorias.existsById(menu.getCategoria().getId())) {
            attributes.addFlashAttribute("error", "Selecciona una categoría registrada en MySQL.");
            return "redirect:/menu";
        }
        if (fotoArchivo != null && !fotoArchivo.isEmpty()) {
            menu.setFoto(guardarFoto(fotoArchivo));
        } else if (menu.getId() != null) {
            service.buscarPorId(menu.getId()).ifPresent(actual -> menu.setFoto(actual.getFoto()));
        }
        service.guardar(menu);
        return "redirect:/menu";
    }

    @PostMapping("/menu/eliminar/{id}")
    public String eliminar(@PathVariable Integer id) { service.eliminar(id); return "redirect:/menu"; }

    @PostMapping("/menu/actualizar/{id}")
    public String actualizar(@PathVariable Integer id, @ModelAttribute Menu menu,
                              @RequestParam(value = "fotoArchivo", required = false) MultipartFile fotoArchivo,
                              RedirectAttributes attributes) {
        menu.setId(id);
        return guardar(menu, fotoArchivo, attributes);
    }

    private String guardarFoto(MultipartFile archivo) {
        try {
            Files.createDirectories(CARPETA_FOTOS);
            String extension = "";
            String original = archivo.getOriginalFilename();
            if (original != null && original.contains(".")) {
                extension = original.substring(original.lastIndexOf('.'));
            }
            String nombreArchivo = UUID.randomUUID() + extension;
            Path destino = CARPETA_FOTOS.resolve(nombreArchivo);
            Files.copy(archivo.getInputStream(), destino, StandardCopyOption.REPLACE_EXISTING);
            return "/uploads/menu/" + nombreArchivo;
        } catch (IOException ex) {
            throw new IllegalStateException("No se pudo guardar la foto del producto", ex);
        }
    }
}