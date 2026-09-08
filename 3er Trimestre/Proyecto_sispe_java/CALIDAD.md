# Métricas de calidad SISPE

## 1. Cobertura con JaCoCo

Desde esta carpeta ejecuta en Windows:

```bash
.\mvnw.cmd clean verify
```

En PowerShell usa el mismo comando. La medición actual cuenta 45 pruebas
unitarias con JUnit y Mockito. JaCoCo excluye únicamente configuración y clase
de arranque del porcentaje funcional (`config/**` y
`SpringbootWebApplication.java`). Resultado actual: aproximadamente `86.18%`
de instrucciones y `85.44%` de líneas, por encima del umbral Maven de `80%`.

Reportes generados:

- `target/site/jacoco/index.html`: cobertura navegable por paquete, clase y método.
- `target/site/jacoco/jacoco.xml`: reporte XML consumido por SonarQube.
- `target/surefire-reports`: resultados de pruebas JUnit.

El `jacoco:check` bloquea la compilación si la cobertura funcional cae por
debajo de `80%`. La cobertura no sustituye pruebas de aceptación, DAST o
pentesting.

## 2. SonarQube local

La opción recomendada para este proyecto académico es SonarQube Community local:
mantiene el código y los hallazgos en el equipo, y permite repetir el análisis
sin depender de una cuenta externa. Requiere Docker Desktop:

```bash
docker compose -f docker-compose.sonarqube.yml up -d
```

Abre `http://localhost:9000`. En el primer acceso, usa `admin` / `admin` y cambia la contraseña. Crea un token en **My Account > Security** y ejecútalo fuera del repositorio:

```bash
$env:SONAR_TOKEN = 'tu-token'
.\mvnw.cmd clean verify sonar:sonar -Dsonar.token="$env:SONAR_TOKEN"
```

También se puede indicar explícitamente la URL y la clave:

```bash
.\mvnw.cmd clean verify sonar:sonar `
  -Dsonar.host.url=http://localhost:9000 `
  -Dsonar.projectKey=sispe-springboot `
  -Dsonar.token="$env:SONAR_TOKEN"
```

## 3. Matriz automática de bugs

Después del análisis, exporta los hallazgos abiertos:

```bash
$env:SONAR_HOST_URL = 'http://localhost:9000'
$env:SONAR_PROJECT_KEY = 'sispe-springboot'
$env:SONAR_TOKEN = 'tu-token'
python scripts/sonarqube-issues.py
```

Se generan `target/sonarqube/matriz-hallazgos.csv` y `target/sonarqube/matriz-hallazgos.json`, con clave, tipo, severidad, estado, mensaje, archivo/componente, línea, regla y fecha.

## 4. Seguridad y PDCA

- **Plan**: se definieron ISO/IEC 25010, desarrollo seguro y un umbral de cobertura.
- **Do**: se añadieron pruebas unitarias y JaCoCo; las contraseñas se validan exclusivamente con BCrypt.
- **Check**: `mvn verify` ejecuta pruebas, cobertura y el umbral; SonarQube debe revisar bugs, vulnerabilidades y code smells.
- **Act**: exportar la matriz de hallazgos y corregir cualquier vulnerabilidad High/Critical antes de producción.

La base de datos debe migrar las contraseñas históricas en texto plano a hashes
BCrypt antes de desplegar esta versión; el encoder ya no acepta texto plano.

## 5. Interpretación

- **Bugs**: defectos que pueden provocar comportamiento incorrecto.
- **Vulnerabilities**: riesgos de seguridad.
- **Code smells**: problemas de mantenibilidad.
- **Coverage**: porcentaje de instrucciones cubiertas por pruebas.
- **Quality Gate**: resultado global de las condiciones configuradas en SonarQube.

No se versionan tokens ni reportes generados en `target/`.
