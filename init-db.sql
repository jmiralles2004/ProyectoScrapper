-- Esquema inicial de base de datos

-- Activar extensión pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS users (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),  -- ID único
    email           VARCHAR(255) UNIQUE NOT NULL,  -- Email único
    hashed_password VARCHAR(255) NOT NULL,  -- Contraseña encriptada
    is_active       BOOLEAN     NOT NULL DEFAULT TRUE,  -- Estado de usuario
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),  -- Fecha de creación
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()   -- Fecha de actualización
);

-- Índice para búsquedas rápidas por email
CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);

-- Actualizar timestamp automáticamente
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para actualizar el campo updated_at en cada actualización de la tabla users
CREATE OR REPLACE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION set_updated_at();