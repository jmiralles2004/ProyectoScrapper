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

-- Tabla de perfiles (Fase 2)
CREATE TABLE IF NOT EXISTS profiles (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),  -- ID único del perfil
    user_id         UUID        NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,  -- Usuario dueño del perfil
    cv_filename     VARCHAR(255) NOT NULL,  -- Nombre original del PDF
    cv_text         TEXT        NOT NULL,  -- Texto extraído del CV
    cv_object_key   VARCHAR(512) NOT NULL UNIQUE,  -- Ruta del JSON en MinIO
    storage_bucket  VARCHAR(100) NOT NULL DEFAULT 'profiles',  -- Bucket de MinIO
    desired_role    VARCHAR(120),  -- Rol objetivo declarado para cambio profesional
    transition_summary TEXT,  -- Contexto del cambio profesional deseado
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Compatibilidad para entornos ya inicializados antes de Fase 8
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS desired_role VARCHAR(120);
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS transition_summary TEXT;

-- Índices para consultas frecuentes de perfiles
CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON profiles (user_id);
CREATE INDEX IF NOT EXISTS idx_profiles_created_at ON profiles (created_at DESC);

-- Trigger para updated_at en la tabla profiles
CREATE OR REPLACE TRIGGER trg_profiles_updated_at
    BEFORE UPDATE ON profiles
    FOR EACH ROW
    EXECUTE FUNCTION set_updated_at();