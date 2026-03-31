# Explicación de la Estructura - Fase 7

## 📋 Descripción General
Fase 7 añade una **capa de documentación OpenAPI/Swagger por gateway** al proyecto JobMatch. Esta fase no introduce lógica de negocio nueva: publica de forma estable la documentación técnica de Auth, Profile e Integration detrás de Nginx para facilitar frontend, QA e integraciones.

---

### `docker-compose.yml` → ⚠️ No eliminar (CRÍTICO)
**Propósito**: Integrar el contenedor dedicado de documentación.

**Puntos clave de Fase 7**:
- Nuevo servicio `swagger-ui`.
- Selector centralizado de contratos OpenAPI para los 3 microservicios.

---

### `nginx-proxy/nginx.conf` → ⚠️ No eliminar (CRÍTICO)
**Propósito**: Publicar la documentación centralizada por gateway.

**Rutas de Fase 7**:
- `/swagger/`
- `/auth/docs`, `/profiles/docs`, `/integration/docs`
- `/auth/openapi.json`, `/profiles/openapi.json`, `/integration/openapi.json`

---

### `services/auth-service/app/main.py` → ⚠️ No eliminar (CRÍTICO)
**Propósito**: Exponer documentación del servicio de autenticación bajo prefijo público.

**Rutas añadidas en Fase 7**:
- `/auth/docs`
- `/auth/openapi.json`

---

### `services/profile-service/app/main.py` → ⚠️ No eliminar (CRÍTICO)
**Propósito**: Exponer documentación del servicio de perfiles bajo prefijo público.

**Rutas añadidas en Fase 7**:
- `/profiles/docs`
- `/profiles/openapi.json`

---

### `services/integration-service/app/main.py` → ⚠️ No eliminar (CRÍTICO)
**Propósito**: Exponer documentación del servicio de integración bajo prefijo público.

**Rutas añadidas en Fase 7**:
- `/integration/docs`
- `/integration/openapi.json`

---

### `endpoints.md` → ⚠️ No eliminar (CRÍTICO)
**Propósito**: Documentar el contrato global, incluyendo endpoints funcionales y documentales.

**Puntos clave de Fase 7**:
- Se incorpora sección dedicada a Swagger/OpenAPI por gateway.
- Se aclara que no hay endpoints de negocio nuevos en esta fase.
- Se añade nota de seguridad para producción.

---

### `fases.md` → ⚠️ No eliminar (CRÍTICO)
**Propósito**: Registrar oficialmente Fase 7 y sus entregables.

**Puntos clave de Fase 7**:
- Nueva definición de fase en la hoja maestra.
- Instrucción actual actualizada a Fase 7.
- Registro operativo documental de cierre.

---

### `Fase7/` → ⚠️ No eliminar (CRÍTICO)
**Propósito**: Contiene la documentación oficial y el respaldo inmutable de Fase 7.

**Archivos esperados**:
- `README.md`
- `ENDPOINTS.md`
- `criterios-aceptacion.md`
- `explicacion-archivos.md`
- `_backup_phase7_base/`

---

## ✅ Hechos clave
- Fase 7 mejora gobernanza y trazabilidad API sin cambiar lógica de negocio.
- La documentación queda servida bajo rutas estables por dominio funcional.
- Existe portal unificado `/swagger/` para navegar todos los contratos desde una sola UI.
- Frontend y QA pueden consumir OpenAPI JSON sin acoplarse a puertos internos.

---

## Validación obligatoria y evidencia operativa

### Qué se valida en Fase 7
- Que Swagger UI responde por prefijo en los tres servicios.
- Que OpenAPI JSON responde por prefijo en los tres servicios.
- Que los endpoints funcionales existentes siguen operativos.

### Recomendación de seguridad
- En producción, proteger `/auth/docs`, `/profiles/docs`, `/integration/docs` y sus JSON con autenticación, allowlist de red o ambos.
