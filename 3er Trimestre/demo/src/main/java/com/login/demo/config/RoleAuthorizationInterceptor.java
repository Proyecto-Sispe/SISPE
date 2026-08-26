package com.login.demo.config;

import com.login.demo.model.Usuario;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.servlet.http.HttpSession;
import org.springframework.web.servlet.HandlerInterceptor;

import java.util.List;

public class RoleAuthorizationInterceptor implements HandlerInterceptor {
    private final List<String> admin = List.of("/usuarios", "/mesas", "/menu", "/facturas", "/reportes");
    private final List<String> kitchen = List.of("/cocina");
    private final List<String> waiter = List.of("/pedidos", "/mesas");

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
        String path = request.getRequestURI();
        if (path.startsWith("/css/") || path.startsWith("/js/") || path.startsWith("/images/")
                || path.equals("/login") || path.startsWith("/cliente/escanear")
                || path.startsWith("/registro") || path.startsWith("/password")
                || path.equals("/menu/digital") || path.startsWith("/error")) return true;

        HttpSession session = request.getSession(false);
        Usuario usuario = session == null ? null : (Usuario) session.getAttribute("usuario");
        if (usuario == null) {
            response.sendRedirect("/login");
            return false;
        }
        String role = String.valueOf(session.getAttribute("rol"));
        if (matches(path, admin) && !role.equals("Administrador")) return forbidden(response);
        if (matches(path, kitchen) && !role.equals("Cocinero") && !role.equals("Administrador")) return forbidden(response);
        if (matches(path, waiter) && !role.equals("Mesero") && !role.equals("Administrador")) return forbidden(response);
        if (path.startsWith("/cliente/") && !role.equals("Cliente") && !role.equals("Mesero") && !role.equals("Administrador")) return forbidden(response);
        return true;
    }

    private boolean matches(String path, List<String> prefixes) { return prefixes.stream().anyMatch(path::startsWith); }
    private boolean forbidden(HttpServletResponse response) throws Exception { response.sendError(403, "No autorizado"); return false; }
}
