# 📦 Backup - Fase 0 (Base Inmutable)

## Propósito
Esta carpeta contiene **copias de seguridad** de los archivos base de **Fase 0** que definen la infraestructura inicial.

⚠️ **IMPORTANTE**: Estos archivos definen la infraestructura y **NO DEBEN SER MODIFICADOS** en futuras fases.

## Archivos incluidos

| Archivo | Propósito |
|---------|----------|
| `phase0_docker-compose.yml` | Configuración de todos los servicios Docker |
| `phase0_.env.docker` | Variables de entorno para Docker |
| `phase0_init-db.sql` | Script de inicialización de PostgreSQL |
| `phase0_Dockerfile_nginx` | Dockerfile del servidor Nginx |
| `phase0_nginx.conf` | Configuración de Nginx |
| `phase0_explicacion-archivos.md` | Documentación de la estructura |

## 🔐 Por qué este backup es crítico

- **Base inmutable**: Define cómo arrancan los servicios en Docker
- **Referencia histórica**: Si algo se rompe, puedes comparar con estos archivos originales
- **Validación**: Asegura que cada fase parte de la misma infraestructura

## ⚠️ Cuándo usar este backup

✅ **Úsalo para**:
- Verificar que la infraestructura original funciona
- Comparar cambios en futuras fases
- Restaurar la configuración original si algo se daña

❌ **NO lo uses para**:
-Modificar la infraestructura (los archivos reales están fuera de esta carpeta)
- Ignorar cambios necesarios en el código

## 🔄 Flujo de fases

1. **Fase 0** ✅ (Este commit)
   - Infraestructura base
   - Este backup se crea

2. **Fase 1** (Próximo commit)
   - Usará la infraestructura de Fase 0
   - Agregará: Autenticación, usuarios, etc.
   - Su propio commit

3. **Fase 2+**
   - Misma dinámica
   - Cada fase su commit

---

**Creado**: 26 de marzo de 2026
**Estado**: Producción
