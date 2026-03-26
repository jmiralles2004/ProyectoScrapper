# 🔌 Endpoints de JobMatch - Fase 0

## Descripción General
Endpoints disponibles en la **infraestructura base (Fase 0)**.

---

## 🏗️ FASE 0 - Infraestructura Base

**Estado**: ✅ Activo  
**Propósito**: Validar que la infraestructura funciona

| Método | Ruta | Servicio | Descripción |
|--------|------|---------|------------|
| `GET` | `/health` | Nginx | Verifica que Nginx está vivo (Docker healthcheck) |

**Ejemplo**:
```bash
curl http://localhost/health
```

**Respuesta** (HTTP 200):
```json
{"status":"ok","service":"nginx-proxy"}
```

---

## 📝 Notas
- Este es el **único endpoint de Fase 0**
- Se usa para validar que la infraestructura está operativa
- Todos los demás endpoints se agregarán en fases futuras