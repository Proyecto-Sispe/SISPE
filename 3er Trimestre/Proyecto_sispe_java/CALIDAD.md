# Métricas de calidad SISPE

## 1. Cobertura con JaCoCo

Desde esta carpeta ejecuta:

```bash
mvn clean verify
```

Reportes generados:

- `target/site/jacoco/index.html`: cobertura navegable por paquete, clase y método.
- `target/site/jacoco/jacoco.xml`: reporte XML consumido por SonarQube.
- `target/surefire-reports`: resultados de pruebas JUnit.

El porcentaje real depende de las pruebas existentes y no se fija artificialmente. El `jacoco:check` queda activo para validar la métrica sin bloquear inicialmente el proyecto (`0.00` mínimo); luego puede elevarse cuando haya cobertura base.

## 2. SonarQube local

Requiere Docker Desktop o Docker Engine:

```bash
docker compose -f docker-compose.sonarqube.yml up -d
```

Abre `http://localhost:9000`. En el primer acceso, usa `admin` / `admin` y cambia la contraseña. Crea un token en **My Account > Security** y ejecútalo fuera del repositorio:

```bash
export SONAR_TOKEN='tu-token'
mvn clean verify sonar:sonar -Dsonar.token="$SONAR_TOKEN"
```

También se puede indicar explícitamente la URL y la clave:

```bash
mvn clean verify sonar:sonar \
  -Dsonar.host.url=http://localhost:9000 \
  -Dsonar.projectKey=sispe-springboot \
  -Dsonar.token="$SONAR_TOKEN"
```

## 3. Matriz automática de bugs

Después del análisis, exporta los hallazgos abiertos:

```bash
export SONAR_HOST_URL=http://localhost:9000
export SONAR_PROJECT_KEY=sispe-springboot
export SONAR_TOKEN='tu-token'
python3 scripts/sonarqube-issues.py
```

Se generan `target/sonarqube/matriz-hallazgos.csv` y `target/sonarqube/matriz-hallazgos.json`, con clave, tipo, severidad, estado, mensaje, archivo/componente, línea, regla y fecha.

## 4. Interpretación

- **Bugs**: defectos que pueden provocar comportamiento incorrecto.
- **Vulnerabilities**: riesgos de seguridad.
- **Code smells**: problemas de mantenibilidad.
- **Coverage**: porcentaje de instrucciones cubiertas por pruebas.
- **Quality Gate**: resultado global de las condiciones configuradas en SonarQube.

No se versionan tokens ni reportes generados en `target/`.
