# Prompt Maestro para Claude - Proyecto JobMatch

## Contexto del Proyecto

### Descripción General
Plataforma que conecta candidatos con ofertas de trabajo mediante IA.
- Usuarios suben CV (PDF) + descripción personal
- Sistema genera embeddings (vectores) de CVs y ofertas
- Calcula porcentaje de match entre CV y ofertas
- Muestra ofertas personalizadas filtradas por match

### Stack Tecnológico
- **Backend**: FastAPI (Python 3.11+)
- **Bases de datos**: PostgreSQL (pgvector), Redis (colas), Qdrant (vectores)
- **Almacenamiento**: MinIO (JSON de CVs)
- **IA/ML**: sentence-transformers (all-MiniLM-L6-v2, 384 dims)
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
│ ├── embedding-service/
│ ├── offer-service/
│ └── matching-service/
└── tests/
└── e2e/


---

## Principios de Desarrollo (NO NEGOCIABLES)

### 1. Segmentación por Fases
- Cada fase es un entregable **100% funcional y testeado**
- Una fase terminada = **se sube a GitHub con tag** y NO se vuelve a tocar
- Las fases son independientes y pueden desarrollarse en paralelo (con mocks)

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
- PostgreSQL, Redis, MinIO, Qdrant, Nginx
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

### FASE 3: Embedding Service
- Generación de embeddings (sentence-transformers)
- Workers con Redis
- Qdrant client
- Colecciones `cvs` y `offers`
- Tests de embeddings

### FASE 4: Offer Service
- CRUD de ofertas
- Trigger de embeddings al crear oferta
- Tabla `offers`
- Tests de CRUD

### FASE 5: Matching Service
- Cálculo de similitud coseno
- Almacenamiento de matches
- Endpoints de consulta personalizada
- Tabla `matches`
- Tests de matching

### FASE 6: Integración Final
- Endpoints compuestos (ofertas personalizadas con match)
- Webhooks entre servicios
- Tests E2E


---

## Instrucción Actual

**FASE A DESARROLLAR: [FASE 0 - Infraestructura Base]**

Actúa como mi Arquitecto de Proyectos IT y desarrolla esta fase siguiendo todos los principios anteriores.

Entregables requeridos:
1. docker-compose.yml completo y funcional
2. .env.example con todas las variables
3. init-db.sql con esquema inicial (solo tabla users de momento)
4. nginx-proxy/Dockerfile y nginx.conf
5. Healthchecks para todos los servicios
6. Tests de infraestructura (conexiones entre servicios)
7. README.md con instrucciones para levantar todo
8. Checklist de criterios de aceptación

Asegúrate de:
- No repetir código
- Usar type hints
- Incluir docstrings
- Los tests deben pasar
- Todo debe estar documentado

Empieza.