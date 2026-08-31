package com.sispe.springboot_web.Service;

import com.sispe.springboot_web.Model.PasswordReset;
import com.sispe.springboot_web.Model.Persona;
import com.sispe.springboot_web.Repository.PasswordResetRepository;
import com.sispe.springboot_web.Repository.PersonaRepository;
import jakarta.mail.MessagingException;
import jakarta.mail.internet.MimeMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.MimeMessageHelper;
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
        MimeMessage mensaje = mailSender.createMimeMessage();

        try {
            MimeMessageHelper helper = new MimeMessageHelper(mensaje, false, "UTF-8");
            helper.setTo(correo);
            helper.setSubject("SISPE | Código para recuperar tu contraseña");
            helper.setText("""
                    <!doctype html>
                    <html lang="es">
                    <body style="margin:0;background:#f1f5f9;font-family:Arial,Helvetica,sans-serif;color:#102a43;">
                      <div style="padding:32px 16px;">
                        <div style="max-width:560px;margin:0 auto;background:#ffffff;border:1px solid #d9e2ec;border-radius:18px;overflow:hidden;">
                          <div style="background:#2563eb;padding:28px 32px;color:#ffffff;">
                            <div style="font-size:13px;font-weight:bold;letter-spacing:3px;">SISPE</div>
                            <h1 style="margin:18px 0 0;font-size:25px;line-height:1.25;">Recupera tu contraseña</h1>
                          </div>
                          <div style="padding:32px;">
                            <p style="margin:0 0 14px;font-size:16px;line-height:1.6;">Recibimos una solicitud para restablecer tu contraseña.</p>
                            <p style="margin:0 0 10px;font-size:14px;color:#627d98;">Tu código de verificación es:</p>
                            <div style="margin:0 0 24px;padding:18px;text-align:center;background:#eff6ff;border:1px solid #bfdbfe;border-radius:12px;color:#1d4ed8;font-size:32px;font-weight:bold;letter-spacing:8px;">%s</div>
                            <p style="margin:0 0 10px;font-size:14px;line-height:1.6;color:#486581;">Este código vence en <strong>%d minutos</strong>.</p>
                            <p style="margin:24px 0 0;padding-top:20px;border-top:1px solid #e5e7eb;font-size:13px;line-height:1.6;color:#829ab1;">Si tú no solicitaste este cambio, puedes ignorar este correo. Tu contraseña no se modificará.</p>
                          </div>
                          <div style="padding:18px 32px;background:#f8fafc;text-align:center;color:#829ab1;font-size:12px;">Mensaje automático de SISPE. Por favor, no respondas a este correo.</div>
                        </div>
                      </div>
                    </body>
                    </html>
                    """.formatted(codigo, MINUTOS_VALIDEZ), true);
            mailSender.send(mensaje);
        } catch (MessagingException ex) {
            throw new IllegalStateException("No se pudo preparar el correo de recuperación.", ex);
        }
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
