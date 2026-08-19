package com.login.demo.controller;
import org.springframework.stereotype.Controller; import org.springframework.ui.Model; import org.springframework.web.bind.annotation.*;
@Controller public class InicioController { @GetMapping({"/","/inicio"}) public String inicio(Model model){model.addAttribute("titulo","Sistema Restaurante"); return "inicio";} @GetMapping("/login") public String login(){return "login";} @GetMapping("/dashboard") public String dashboard(){return "dashboard";} }
