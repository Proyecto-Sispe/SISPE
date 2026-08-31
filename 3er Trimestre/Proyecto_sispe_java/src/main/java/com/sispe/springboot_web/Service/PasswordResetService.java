package com.sispe.springboot_web.Service;

import com.sispe.springboot_web.Model.PasswordReset;
import com.sispe.springboot_web.Model.Persona;
import com.sispe.springboot_web.Repository.PasswordResetRepository;
import com.sispe.springboot_web.Repository.PersonaRepository;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.security.SecureRandom;
import java.time.LocalDateTime;
import java.util.Optional;
import java.util.UUID;

@Service
public class PasswordResetService {

    private static final int MINUTOS_VALIDEZ = 15;
    private final SecureRandom random = new SecureRandom();

    private final PersonaRepository personaRepository;
    private final PasswordResetRepository resetRepository;
    private final PasswordEncoder passwordEncoder;
    private final JavaMailSender mailSender;

    public PasswordResetService(PersonaRepository personaRepository,
                                 PasswordResetRepository resetRepository,
                                 PasswordEncoder passwordEncoder,
                                 JavaMailSender mailSender) {
        this.personaRepository = personaRepository;
        this.resetRepository = resetRepository;
        this.passwordEncoder = passwordEncoder;
        this.mailSender = mailSender;
    }

    @Transactional
    public void solicitarCodigo(String correo) {
        Optional<Persona> persona = personaRepository.findByCorreo(correo.trim());
        if (persona.isEmpty()) {
            return;
        }

        String codigo = String.format("%06d", random.nextInt(1_000_000));

        PasswordReset reset = PasswordReset.builder()
                .correo(correo.trim())
                .token(UUID.randomUUID().toString())
                .codigo(codigo)
                .expira(LocalDateTime.now().plusMinutes(MINUTOS_VALIDEZ))
                .usado(false)
                .createdAt(LocalDateTime.now())
                .build();

        resetRepository.save(reset);
        enviarCorreo(correo.trim(), codigo);
    }

    private void enviarCorreo(String correo, String codigo) {
        SimpleMailMessage mensaje = new SimpleMailMessage();
        mensaje.setTo(correo);
        mensaje.setSubject("SISPE - Código para recuperar tu contraseña");
        mensaje.setText(
                "Recibimos una solicitud para restablecer tu contraseña.\n\n" +
                "Tu código de verificación es: " + codigo + "\n\n" +
                "Este código vence en " + MINUTOS_VALIDEZ + " minutos.\n" +
                "Si tú no solicitaste esto, puedes ignorar este correo."
        );
        mailSender.send(mensaje);
    }

    @Transactional
    public void restablecerPassword(String correo, String codigo, String nuevaPassword) {
        PasswordReset reset = resetRepository
                .findFirstByCorreoAndUsadoFalseOrderByCreatedAtDesc(correo.trim())
                .orElseThrow(() -> new IllegalArgumentException("No hay una solicitud de recuperación activa para ese correo."));

        if (Boolean.TRUE.equals(reset.getUsado())) {
            throw new IllegalArgumentException("Este código ya fue utilizado. Solicita uno nuevo.");
        }
        if (reset.getExpira().isBefore(LocalDateTime.now())) {
            throw new IllegalArgumentException("El código expiró. Solicita uno nuevo.");
        }
        if (!reset.getCodigo().equals(codigo.trim())) {
            throw new IllegalArgumentException("El código ingresado no es correcto.");
        }

        Persona persona = personaRepository.findByCorreo(correo.trim())
                .orElseThrow(() -> new IllegalArgumentException("La cuenta ya no existe."));

        persona.setPassword(passwordEncoder.encode(nuevaPassword));
        personaRepository.save(persona);

        reset.setUsado(true);
        resetRepository.save(reset);
    }
}