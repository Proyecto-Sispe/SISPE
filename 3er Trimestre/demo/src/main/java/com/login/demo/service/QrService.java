package com.login.demo.service;

import com.google.zxing.BarcodeFormat;
import com.google.zxing.WriterException;
import com.google.zxing.client.j2se.MatrixToImageWriter;
import com.google.zxing.common.BitMatrix;
import com.google.zxing.qrcode.QRCodeWriter;
import org.springframework.stereotype.Service;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.util.Base64;

@Service
public class QrService {
    public byte[] generarPng(String contenido) {
        try {
            BitMatrix matrix = new QRCodeWriter().encode(contenido, BarcodeFormat.QR_CODE, 320, 320);
            ByteArrayOutputStream output = new ByteArrayOutputStream();
            MatrixToImageWriter.writeToStream(matrix, "PNG", output);
            return output.toByteArray();
        } catch (WriterException | IOException exception) {
            throw new IllegalStateException("No se pudo generar el código QR", exception);
        }
    }

    public String generarDataUri(String contenido) {
        return "data:image/png;base64," + Base64.getEncoder().encodeToString(generarPng(contenido));
    }
}
