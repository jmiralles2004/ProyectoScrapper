# Explicación de la Estructura - Fase 0

## 📋 Descripción General
Fase 0 es la **infraestructura base** del proyecto JobMatch. Aquí se definen todos los servicios (base de datos, caché, almacenamiento) que funcionan en contenedores Docker y se comunican entre sí.

---

### `nginx-proxy/` → ⚠️ No eliminar (CRÍTICO)
**Propósito**: Nginx es la "puerta de entrada" de toda la aplicación. Recibe todas las solicitudes HTTP y las dirige al servicio correcto.

**Archivos**:
- `Dockerfile`: Define cómo se construye el contenedor de Nginx
- `nginx.conf`: Configura las reglas de Nginx:
  - Ruta `/health` → Verifica que Nginx está vivo (Docker healthcheck)
  - Otras rutas → Retorna 404 (error no encontrado)

---

### `.env` → ⚠️ No eliminar (CRÍTICO)
**Propósito**: Define variables de entorno para desarrollo LOCAL (sin Docker).

**Variables principales**:
- `DATABASE_URL=postgresql://jobmatch_user:jobmatch_pass@localhost:5432/jobmatch`
- `REDIS_URL=redis://:redis_pass@redis:6379/0`
- `MINIO_ENDPOINT=localhost:9000`
- `QDRANT_HOST=localhost`

---

### `.env.docker` → ⚠️ No eliminar (está en .gitignore, CRÍTICO)
**Propósito**: Define variables de entorno para desarrollo CON Docker Compose.

**Diferencia principal**: Usa nombres de servicios en lugar de localhost:
- `DATABASE_URL=postgresql://jobmatch_user:jobmatch_pass@postgres:5432/jobmatch` ← postgres (nombre del servicio)
- `MINIO_ENDPOINT=minio:9000` ← minio (nombre del servicio)

---

### `docker-compose.yml` → ⚠️ No eliminar (CRÍTICO)
**Propósito**: Define todos los 5 servicios que corren en contenedores Docker.

#### 🐘 PostgreSQL (Base de datos)
- **Contenedor**: jobmatch-postgres
- **Puerto**: 5432
- **¿Qué hace?**: Almacena toda la información del sistema
- **Datos persistentes**: Volumen `postgres_data`
- **Extras**: Incluye extensión pgvector para vectores de IA

#### ⚡ Redis (Caché/Cola de mensajes)
- **Contenedor**: jobmatch-redis
- **Puerto**: 6379
- **¿Qué hace?**: Almacena datos en memoria rápidamente
- **Datos persistentes**: Volumen `redis_data`

#### 📦 MinIO (Almacenamiento de archivos)
- **Contenedor**: jobmatch-minio
- **Puertos**: 
  - 9000 → API (guardar/descargar archivos)
  - 9001 → Panel web (visualizar archivos)
- **¿Qué hace?**: Almacena archivos (CVs, documentos)
- **Datos persistentes**: Volumen `minio_data`

#### 🔍 Qdrant (Base de datos vectorial - IA)
- **Contenedor**: jobmatch-qdrant
- **Puerto**: 6333
- **¿Qué hace?**: Almacena vectores para búsquedas inteligentes (ej: "trabajos similares")
- **Datos persistentes**: Volumen `qdrant_data`

#### 🚪 Nginx (Proxy/Guardia de entrada)
- **Contenedor**: jobmatch-nginx
- **Puerto**: 80 (HTTP)
- **¿Qué hace?**: Recibe solicitudes y las dirige al servicio correcto
- **Importante**: Solo inicia cuando TODOS los otros servicios están saludables

#### 🌐 Red compartida
Todos los contenedores están en la red `jobmatch-network`, por eso pueden comunicarse usando nombres:
- `postgres:5432` (en lugar de localhost:5432)
- `minio:9000` (en lugar de localhost:9000)

---

### `init-db.sql` → ⚠️ No eliminar (CRÍTICO)
**Propósito**: Script que se ejecuta **una sola vez** cuando PostgreSQL se inicia por primera vez. Crea la estructura inicial.

**¿Qué hace?**:
1. Activa la extensión `pgvector` → Habilita soporte para vectores de IA
2. Crea la tabla `users` → Tabla de usuarios con campos:
   - `id` (UUID único)
   - `email` (único)
   - `hashed_password` (encriptada)
   - `is_active` (boolean)
   - `created_at` (fecha creación)
   - `updated_at` (fecha última actualización)
3. Crea índice en `email` → Búsquedas por email son muy rápidas
4. Crea un "disparador" automático → Actualiza `updated_at` cada vez que modificas un usuario

---

## 🔄 Flujo de arranque

1. **docker compose up -d --build** inicia:
   - PostgreSQL (se ejecuta `init-db.sql` automáticamente)
   - Redis
   - MinIO
   - Qdrant
   - Nginx **(espera a que todos los anteriores estén saludables)**

2. **Docker verifica salud** con healthchecks cada 10 segundos

3. **Nginx recibe solicitudes** y las encamina:
   - `/health` → Responde "estoy vivo" (HTTP 200)
   - Otras rutas → Responde "no encontrado" (HTTP 404)

---

## ✅ Hechos clave
- Todos los datos **persisten** en volúmenes (no se pierden al reiniciar)
- Los servicios se comunican por **nombres** (postgres, redis, etc.), no por IP
- Todo está en castellano en comentarios para claridad
- Hay **10 tests** que validan cada servicio funciona correctamente

---

## 🔌 Endpoints de Fase 0

**Fase 0 solo expone UN endpoint**. Es muy básico porque solo verifica infraestructura:

| Método | Ruta | Servicio | Propósito |
|--------|------|---------|----------|
| `GET` | `/health` | Nginx | Verifica que Nginx está vivo (Docker healthcheck) |

**Ejemplo de uso**:
```bash
curl http://localhost/health
```

**Respuesta esperada**:
```json
{"status":"ok","service":"nginx-proxy"}
```

**¿Por qué solo esto?**

Fase 0 es **solo infraestructura**. En fases futuras añadirás:
- Fase 1: API de autenticación (login, registro)
- Fase 2: API de perfiles (perfil de usuario)
- Fase 3: API de búsqueda de trabajos
- etc.

Por ahora, Nginx solo valida su propia salud. Todas las otras solicitudes retornan 404.

---