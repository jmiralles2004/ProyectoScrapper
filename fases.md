# Prompt Maestro para Claude - Proyecto JobMatch

## Contexto del Proyecto

### Descripción General
Plataforma que conecta candidatos con ofertas de trabajo mediante IA.
- Usuarios suben CV (PDF) + descripción personal
- Sistema recopila ofertas desde un proveedor externo
- Sistema muestra ofertas priorizadas en base al perfil del cliente

### Stack Tecnológico
- **Backend**: FastAPI (Python 3.11+)
- **Bases de datos**: PostgreSQL
- **Almacenamiento**: MinIO (JSON de CVs)
- **IA/ML**: Integración con proveedor externo (fuera de este repositorio)
- **Proxy/Gateway**: Nginx
- **Contenedores**: Docker + Docker Compose
- **Tests**: pytest con cobertura > 85%
- **Versionado**: GitHub (tags semánticos por fase)

### Estructura de Carpetas (Monorepo)
jobmatch/
├── docker-compose.yml
├── .env.example
├── init-db.sql
├── nginx-proxy/
│ ├── Dockerfile
│ └── nginx.conf
├── services/
│ ├── auth-service/
│ ├── profile-service/
│ └── integration-service/
└── tests/
└── e2e/


---

## Principios de Desarrollo (NO NEGOCIABLES)

### 1. Segmentación por Fases
- Cada fase es un entregable **100% funcional y testeado**
- Una fase terminada = **se sube a GitHub con tag** y NO se vuelve a tocar
- Las fases son independientes y pueden desarrollarse en paralelo (con mocks)
- Al cerrar una fase, también se escribe su `explicacion-archivos.md` con el mismo estilo de la Fase 0 y se crea su copia inmune en `FaseN/_backup_phaseN_base/`
- Al cerrar y publicar una fase, la limpieza del working tree se hace de forma segura: solo se preparan cambios de la fase actual y **nunca** se tocan ni se arrastran cambios de fases anteriores.

### 2. Calidad de Código
- **NO repetir código**: funciones, clases, atributos, variables
- Todo debe ser **DRY (Don't Repeat Yourself)**
- Nombres de variables/funciones en **inglés**, claros y descriptivos
- Type hints en **todas** las funciones
- Docstrings en **todas** las funciones públicas

### 3. Tests
- Cada endpoint debe tener **tests unitarios** completos
- Cobertura mínima: **85%**
- Tests deben ejecutarse en CI (local primero)
- Usar **fixtures** para datos de prueba
- Tests organizados por servicio

### 4. Documentación
- Cada fase genera:
  - `README.md` con instrucciones de ejecución
  - `ENDPOINTS.md` con todos los endpoints documentados
  - `explicacion-archivos.md` con la estructura y el uso de la fase, siguiendo el estilo de Fase 0
  - OpenAPI automático (FastAPI) en `/docs`
- Documentación en **inglés o español** (consistente)

### 5. Endpoints
- RESTful, nombres en plural
- Métodos HTTP correctos: GET (leer), POST (crear), PUT (actualizar), DELETE (eliminar)
- Respuestas JSON con códigos HTTP adecuados (200, 201, 400, 401, 403, 404, 409, 500)
- Autenticación vía JWT en header `Authorization: Bearer <token>`

### 6. Docker
- Cada servicio tiene su propio `Dockerfile`
- Usar imágenes base ligeras (python:3.11-slim)
- Multi-stage build para producción
- Variables de entorno para configuración

### 7. Base de Datos
- Esquema en `init-db.sql` (ejecutado al levantar PostgreSQL)
- Migraciones manuales por ahora (no ORM complejo)
- Usar `asyncpg` para conexiones asíncronas

---

## Formato de Respuesta para Cada Fase

Cuando trabajes en una fase, debes entregar:

1. **Objetivo de la fase** (qué se consigue)
2. **Estructura de carpetas** (árbol de archivos)
3. **Endpoints** (tabla con método, ruta, request, response, códigos)
4. **Esquema de BD** (si aplica, SQL)
5. **Código completo** de cada archivo (con imports, type hints, docstrings)
6. **Tests unitarios** (con pytest, fixtures)
7. **Dockerfile** (si es un servicio nuevo)
8. **README.md** de la fase
9. **ENDPOINTS.md** (documentación para frontend)
10. **Criterios de aceptación** (checklist para dar por terminado)

---

## Fases del Proyecto

### FASE 0: Infraestructura Base
- Docker Compose con todos los servicios
- PostgreSQL, MinIO, Qdrant, Nginx
- Healthchecks y redes configuradas
- Scripts de inicialización

### FASE 1: Auth Service
- Registro, login, JWT
- Tabla `users` en PostgreSQL
- Tests de autenticación

### FASE 2: Profile Service + MinIO
- Subida de CV (PDF)
- Extracción de texto
- Almacenamiento JSON en MinIO
- Tabla `profiles`
- Tests de subida y extracción


### FASE 6: Integración Final
- Recolección de ofertas desde proveedor externo
- Enriquecimiento con datos de perfil del cliente
- Ranking/filtro de ofertas según perfil
- Endpoints compuestos (ofertas personalizadas por cliente)
- Tests E2E

### FASE 7: Documentación OpenAPI/Swagger por Gateway
- Exposicion de Swagger por microservicio via Nginx (`/auth/docs`, `/profiles/docs`, `/integration/docs`)
- Exposicion de contratos OpenAPI JSON por prefijo (`/auth/openapi.json`, `/profiles/openapi.json`, `/integration/openapi.json`)
- Contenedor dedicado `swagger-ui` con portal unificado (`/swagger/`)
- Script integral de validacion de endpoints (`scripts/test_all_endpoints.sh`)
- Contrato API vivo para frontend, QA e integraciones
- Documentacion de fase y backup inmutable con estandares del proyecto


---

## Instrucción Actual

**FASE A DESARROLLAR: [FASE 7 - Documentación OpenAPI/Swagger por Gateway]**

Actúa como mi Arquitecto de Proyectos IT y desarrolla esta fase siguiendo todos los principios anteriores.

Entregables requeridos:
1. Exponer Swagger por gateway para auth/profile/integration
2. Exponer OpenAPI JSON por gateway para auth/profile/integration
3. Integrar contenedor dedicado `swagger-ui` y publicarlo por Nginx en `/swagger/`
4. Mantener compatibilidad de endpoints de negocio existentes
5. Actualizar `endpoints.md` (global) con rutas documentales de Fase 7
6. Crear `Fase7/README.md`, `Fase7/ENDPOINTS.md`, `Fase7/criterios-aceptacion.md`, `Fase7/explicacion-archivos.md`
7. Crear backup inmutable en `Fase7/_backup_phase7_base/`
8. Verificacion basica tecnica de rutas documentales

Asegúrate de:
- No repetir código
- Usar type hints
- Incluir docstrings
- Los tests deben pasar
- Todo debe estar documentado

Empieza.

---

## Registro operativo (2026-03-30) - Cumplimiento documental obligatorio Fase 6

Se deja explicitamente registrado que la informacion de validacion de pruebas, persistencia de datos simulados/reales y readiness de frontend queda documentada en los archivos obligatorios de fase y globales:

- `Fase6/README.md`
- `Fase6/ENDPOINTS.md`
- `Fase6/criterios-aceptacion.md`
- `Fase6/explicacion-archivos.md`
- `Fase6/INTEGRACION_DATOS_EXTERNOS.md`
- `endpoints.md`
- `explicacion-archivos.md`

Incluye:
- Matriz de suites activas y de backup verificadas.
- Diferenciacion de persistencia fake (unit tests) vs persistencia real en Qdrant (smoke test).
- Nota operativa de ejecucion pytest por ruta para evitar colisiones entre backups y servicios activos.
- Backlog de endpoints recomendados para frontend, marcado como pendiente (no implementado).

---

## Registro operativo (2026-03-31) - Cumplimiento documental obligatorio Fase 7

Se deja explicitamente registrado que la capa de documentacion OpenAPI/Swagger por gateway queda documentada en los archivos obligatorios de fase y globales:

- `Fase7/README.md`
- `Fase7/ENDPOINTS.md`
- `Fase7/criterios-aceptacion.md`
- `Fase7/explicacion-archivos.md`
- `endpoints.md`
- `explicacion-archivos.md`

Incluye:
- Rutas Swagger por servicio (`/auth/docs`, `/profiles/docs`, `/integration/docs`).
- Rutas OpenAPI JSON por servicio (`/auth/openapi.json`, `/profiles/openapi.json`, `/integration/openapi.json`).
- Portal unificado Swagger UI por gateway (`/swagger/`).
- Script unico de validacion integral de endpoints (`scripts/test_all_endpoints.sh`).
- Hardening de compose para usar hosts internos entre contenedores en dependencias criticas (MinIO y Qdrant).
- Nota de seguridad para proteger documentacion en produccion (auth o red interna).
- Backup inmutable de fase para trazabilidad y recuperacion.