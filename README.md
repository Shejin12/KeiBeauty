# KeiBeauty Backend - API REST

Backend del e-commerce KeiBeauty para productos K-Beauty (belleza coreana). API REST construida con Flask, PostgreSQL, SQLAlchemy y JWT.

## Stack Tecnológico

- **Python 3.12+**
- **Flask 3.0** - Framework web
- **Flask-SQLAlchemy** - ORM para PostgreSQL
- **Flask-Migrate** - Migraciones de base de datos (Alembic)
- **Flask-JWT-Extended** - Autenticación con tokens JWT
- **Flask-CORS** - Cross-Origin Resource Sharing
- **Gunicorn** - Servidor WSGI para producción
- **PostgreSQL 16** - Base de datos
- **Docker & Docker Compose** - Contenedorización

## Estructura del Proyecto

```
KeiBeauty/
├── app.py                    # Factory de la aplicación Flask
├── config.py                 # Configuración por entornos
├── requirements.txt          # Dependencias Python
├── .env.example             # Variables de entorno de ejemplo
├── Dockerfile               # Multi-stage build para producción
├── docker-compose.yml       # Orquestación local (API + PostgreSQL)
├── seed.py                  # Datos de prueba iniciales
├── models/
│   ├── __init__.py          # Exporta todos los modelos
│   ├── db.py                # Instancia SQLAlchemy
│   ├── usuario.py           # Modelo Usuario (auth, roles)
│   ├── marca.py             # Modelo Marca K-Beauty
│   ├── categoria.py         # Modelo Categoria
│   ├── producto.py          # Modelo Producto
│   ├── carrito.py           # Carrito + DetalleCarrito
│   ├── pedido.py            # Pedido + DetallePedido
│   └── resena.py            # Modelo Resena
├── routes/
│   ├── __init__.py
│   ├── auth.py              # Autenticación (registro, login, perfil)
│   └── products.py          # Productos (CRUD + admin)
└── utils/
    ├── __init__.py
    └── decorators.py        # Decoradores @admin_required, @cliente_required
```

## Requisitos Previos

### Linux (Ubuntu/Debian/Fedora/Arch)

```bash
# Instalar Docker y Docker Compose
sudo apt update && sudo apt install -y docker.io docker-compose-plugin

# O en Fedora:
sudo dnf install -y docker docker-compose

# O en Arch:
sudo pacman -S docker docker-compose

# Iniciar y habilitar Docker
sudo systemctl enable --now docker

# Agregar usuario al grupo docker (reiniciar sesión después)
sudo usermod -aG docker $USER
```

### Windows con WSL2

1. **Instalar WSL2 y Ubuntu:**
   ```powershell
   # En PowerShell como Administrador
   wsl --install -d Ubuntu
   ```

2. **Instalar Docker Desktop para Windows:**
   - Descargar desde: https://www.docker.com/products/docker-desktop/
   - Durante la instalación, habilitar "Use WSL 2 based engine"
   - En Settings > Resources > WSL Integration, habilitar la distribución Ubuntu

3. **Verificar instalación:**
   ```bash
   # Dentro de WSL (Ubuntu)
   docker --version
   docker compose version
   ```

## Configuración Rápida (Docker - Recomendado)

### 1. Clonar y configurar variables de entorno

```bash
git clone git@github.com:Shejin12/KeiBeauty.git
cd KeiBeauty

# Copiar archivo de ejemplo y editar valores
cp .env.example .env
# Editar .env con tus valores (SECRET_KEY, JWT_SECRET_KEY, etc.)
```

### 2. Levantar servicios

```bash
# Construir y levantar en segundo plano
docker compose up --build -d

# Ver logs
docker compose logs -f api

# Ver estado de contenedores
docker compose ps
```

### 3. Inicializar base de datos y seed

```bash
# Crear migración inicial (solo primera vez)
docker compose run --rm api flask db init

# Generar migración
docker compose run --rm api flask db migrate -m "initial migration"

# Aplicar migración
docker compose run --rm api flask db upgrade

# Poblar datos de prueba (marcas, categorías, productos, admin)
docker compose run --rm api python seed.py
```

### 4. Verificar funcionamiento

```bash
# Health check
curl http://localhost:5000/health

# Debería responder:
# {"service":"KeiBeauty API","status":"ok"}
```

## Configuración Manual (Sin Docker - Solo Desarrollo)

### Linux / WSL

```bash
# 1. Instalar PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# 2. Crear base de datos y usuario
sudo -u postgres psql -c "CREATE DATABASE keibeauty_db;"
sudo -u postgres psql -c "CREATE USER postgres WITH PASSWORD 'postgres';"
sudo -u postgres psql -c "ALTER ROLE postgres SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE postgres SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE postgres SET timezone TO 'UTC';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE keibeauty_db TO postgres;"

# 3. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Configurar variables de entorno
cp .env.example .env
# Editar .env con DATABASE_URL=postgresql://postgres:postgres@localhost:5432/keibeauty_db

# 6. Inicializar BD y seed
flask db init
flask db migrate -m "initial migration"
flask db upgrade
python seed.py

# 7. Ejecutar servidor de desarrollo
flask run --host=0.0.0.0 --port=5000
```

### Variables de Entorno (.env)

```env
SECRET_KEY=tu-clave-secreta-super-segura-cambiar-en-produccion
JWT_SECRET_KEY=tu-clave-jwt-super-segura-cambiar-en-produccion
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/keibeauty_db
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173
FLASK_ENV=development
FLASK_APP=app.py
```

## Endpoints de la API

### Autenticación (`/api/auth`)

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| POST | `/registro` | Registrar nuevo usuario | No |
| POST | `/login` | Iniciar sesión | No |
| GET | `/perfil` | Obtener perfil del usuario autenticado | JWT |
| POST | `/refresh` | Renovar access token | JWT (refresh) |

#### POST /api/auth/registro

**Request:**
```json
{
  "nombre": "Juan Perez",
  "email": "juan@test.com",
  "password": "password123",
  "telefono": "+34600111222",
  "direccion_envio": "Calle Test 123"
}
```

**Response (201):**
```json
{
  "mensaje": "Usuario registrado exitosamente.",
  "usuario": {
    "id": 2,
    "nombre": "Juan Perez",
    "email": "juan@test.com",
    "telefono": "+34600111222",
    "direccion_envio": "Calle Test 123",
    "rol": "cliente",
    "fecha_registro": "2026-09-14T02:23:46.506030"
  },
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

#### POST /api/auth/login

**Request:**
```json
{
  "email": "juan@test.com",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "mensaje": "Login exitoso.",
  "usuario": { ... },
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

#### GET /api/auth/perfil

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "usuario": {
    "id": 2,
    "nombre": "Juan Perez",
    "email": "juan@test.com",
    "telefono": "+34600111222",
    "direccion_envio": "Calle Test 123",
    "rol": "cliente",
    "fecha_registro": "2026-09-14T02:23:46.506030"
  }
}
```

#### POST /api/auth/refresh

**Headers:**
```
Authorization: Bearer <refresh_token>
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

### Productos (`/api/products`)

| Método | Endpoint | Descripción | Autenticación | Roles |
|--------|----------|-------------|---------------|-------|
| GET | `/` | Listar productos (filtros: ?categoria=&marca=&buscar=) | No | - |
| GET | `/<id>` | Obtener producto por ID | No | - |
| POST | `/` | Crear producto | JWT | Admin |
| PUT | `/<id>` | Actualizar producto | JWT | Admin |
| DELETE | `/<id>` | Eliminar producto | JWT | Admin |
| GET | `/admin-test` | Test endpoint admin | JWT | Admin |

#### GET /api/products

**Query Parameters (opcionales):**
- `categoria` (int): Filtrar por ID de categoría
- `marca` (int): Filtrar por ID de marca
- `buscar` (string): Buscar por nombre (ILIKE)

**Response (200):**
```json
{
  "data": [
    {
      "id": 1,
      "nombre": "Low pH Good Morning Gel Cleanser",
      "descripcion": "Limpiador gel suave...",
      "ingredientes_clave": "Aceite de arbol de te, BHA, centella asiatica",
      "tipo_piel": "Mixta, grasa, sensible",
      "precio": 14.90,
      "stock": 50,
      "imagen_url": "https://example.com/products/cosrx-cleanser.jpg",
      "estado": "activo",
      "marca_id": 1,
      "categoria_id": 1,
      "marca_nombre": "COSRX",
      "categoria_nombre": "Limpieza",
      "fecha_creacion": "2026-09-14T01:46:23.411889"
    }
  ],
  "message": "Productos obtenidos exitosamente."
}
```

#### GET /api/products/1

**Response (200):**
```json
{
  "data": {
    "id": 1,
    "nombre": "Low pH Good Morning Gel Cleanser",
    "descripcion": "Limpiador gel suave...",
    "ingredientes_clave": "Aceite de arbol de te, BHA, centella asiatica",
    "tipo_piel": "Mixta, grasa, sensible",
    "precio": 14.90,
    "stock": 50,
    "imagen_url": "https://example.com/products/cosrx-cleanser.jpg",
    "estado": "activo",
    "marca_id": 1,
    "categoria_id": 1,
    "marca_nombre": "COSRX",
    "categoria_nombre": "Limpieza",
    "fecha_creacion": "2026-09-14T01:46:23.411889"
  },
  "message": "Producto obtenido exitosamente."
}
```

**Response (404):**
```json
{
  "error": "Producto no encontrado",
  "message": "No existe producto con id 999"
}
```

#### POST /api/products (Admin)

**Headers:**
```
Authorization: Bearer <access_token_admin>
Content-Type: application/json
```

**Request:**
```json
{
  "nombre": "Nuevo Producto Test",
  "descripcion": "Descripción opcional",
  "ingredientes_clave": "Ingredientes opcionales",
  "tipo_piel": "Todo tipo de piel",
  "precio": 25.99,
  "stock": 10,
  "imagen_url": "https://example.com/image.jpg",
  "estado": "activo",
  "marca_id": 1,
  "categoria_id": 2
}
```

**Response (201):**
```json
{
  "data": {
    "id": 6,
    "nombre": "Nuevo Producto Test",
    "descripcion": "Descripción opcional",
    "ingredientes_clave": "Ingredientes opcionales",
    "tipo_piel": "Todo tipo de piel",
    "precio": 25.99,
    "stock": 10,
    "imagen_url": "https://example.com/image.jpg",
    "estado": "activo",
    "marca_id": 1,
    "categoria_id": 2,
    "marca_nombre": "COSRX",
    "categoria_nombre": "Hidratacion",
    "fecha_creacion": "2026-09-14T10:30:00.000000"
  },
  "message": "Producto creado exitosamente."
}
```

**Errores comunes:**
- `400` - Campos obligatorios faltantes / Tipos inválidos / Precio <= 0 / Stock < 0
- `404` - Marca o Categoría no encontrada
- `401` - Token inválido o expirado
- `403` - No es admin

#### PUT /api/products/1 (Admin)

**Headers:**
```
Authorization: Bearer <access_token_admin>
Content-Type: application/json
```

**Request (campos opcionales):**
```json
{
  "nombre": "Nombre actualizado",
  "precio": 29.99,
  "stock": 5,
  "estado": "activo"
}
```

**Response (200):**
```json
{
  "data": { ... producto actualizado ... },
  "message": "Producto actualizado exitosamente."
}
```

#### DELETE /api/products/1 (Admin)

**Headers:**
```
Authorization: Bearer <access_token_admin>
```

**Response (204):**
```json
{
  "data": null,
  "message": "Producto eliminado exitosamente."
}
```

### Carrito (`/api/carrito`)

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| GET | `/` | Obtener carrito del usuario (crea si no existe) | JWT |
| POST | `/items` | Añadir producto al carrito | JWT |
| PUT | `/items/<id>` | Actualizar cantidad de item | JWT |
| DELETE | `/items/<id>` | Eliminar item del carrito | JWT |
| DELETE | `/` | Vaciar carrito | JWT |

#### GET /api/carrito

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "data": {
    "id": 1,
    "usuario_id": 1,
    "fecha_creacion": "2026-09-14T21:07:21.304258",
    "fecha_actualizacion": "2026-09-14T21:11:39.200963",
    "detalles": [
      {
        "id": 1,
        "carrito_id": 1,
        "producto_id": 1,
        "cantidad": 2,
        "fecha_agregado": "2026-09-14T21:08:22.801133",
        "subtotal": 29.8,
        "producto": {
          "id": 1,
          "nombre": "Low pH Good Morning Gel Cleanser",
          "descripcion": "Limpiador gel suave...",
          "ingredientes_clave": "Aceite de arbol de te, BHA, centella asiatica",
          "tipo_piel": "Mixta, grasa, sensible",
          "precio": 14.90,
          "stock": 50,
          "imagen_url": "https://example.com/products/cosrx-cleanser.jpg",
          "estado": "activo",
          "marca_id": 1,
          "categoria_id": 1,
          "marca_nombre": "COSRX",
          "categoria_nombre": "Limpieza",
          "fecha_creacion": "2026-09-14T01:46:23.411889"
        }
      }
    ]
  },
  "message": "Carrito obtenido exitosamente."
}
```

#### POST /api/carrito/items

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request:**
```json
{
  "producto_id": 1,
  "cantidad": 2
}
```

**Response (201):**
```json
{
  "data": {
    "id": 1,
    "usuario_id": 1,
    "fecha_creacion": "2026-09-14T21:07:21.304258",
    "fecha_actualizacion": "2026-09-14T21:08:22.782995",
    "detalles": [
      {
        "id": 1,
        "carrito_id": 1,
        "producto_id": 1,
        "cantidad": 2,
        "fecha_agregado": "2026-09-14T21:08:22.801133",
        "subtotal": 29.8,
        "producto": { ... }
      }
    ]
  },
  "message": "Producto añadido al carrito."
}
```

**Errores comunes:**
- `400` - Cantidad inválida / Stock insuficiente / Producto no activo
- `404` - Producto no encontrado
- `401` - Token inválido o expirado

#### PUT /api/carrito/items/1

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request:**
```json
{
  "cantidad": 3
}
```

**Response (200):**
```json
{
  "data": { ... carrito actualizado ... },
  "message": "Carrito actualizado exitosamente."
}
```

#### DELETE /api/carrito/items/1

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "data": { ... carrito actualizado ... },
  "message": "Item eliminado del carrito."
}
```

#### DELETE /api/carrito

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "data": { ... carrito vacío ... },
  "message": "Carrito vaciado exitosamente."
}
```

## Códigos de Respuesta HTTP

| Código | Descripción |
|--------|-------------|
| 200 | OK - Petición exitosa |
| 201 | Created - Recurso creado |
| 204 | No Content - Eliminado exitosamente |
| 400 | Bad Request - Datos inválidos o faltantes |
| 401 | Unauthorized - Credenciales inválidas o token expirado |
| 403 | Forbidden - Sin permisos (ej. no es admin) |
| 404 | Not Found - Recurso no encontrado |
| 500 | Internal Server Error - Error del servidor |

## Formato de Respuestas

### Éxito
```json
{
  "data": { ... } | [ ... ],
  "message": "Mensaje descriptivo"
}
```

### Error
```json
{
  "error": "Tipo de error",
  "message": "Mensaje descriptivo del error"
}
```

Ejemplos:
- `{"error": "Campos obligatorios faltantes", "message": "Faltan: nombre, precio"}` (400)
- `{"error": "Producto no encontrado", "message": "No existe producto con id 999"}` (404)
- `{"error": "Credenciales inválidas", "message": "Email o contraseña incorrectos"}` (401)
- `{"error": "Acceso denegado", "message": "Se requiere rol de administrador"}` (403)

## Uso del Token JWT

Incluir en el header `Authorization` de cada petición protegida:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

- **Access Token**: Expira en 24 horas (configurable en `JWT_ACCESS_TOKEN_EXPIRES`)
- **Refresh Token**: Expira en 30 días (configurable en `JWT_REFRESH_TOKEN_EXPIRES`)

## Flujo de Recuperación de Contraseña

El sistema implementa un flujo seguro de recuperación de contraseña basado en tokens de un solo uso con expiración.

### Flujo completo paso a paso:

1. **Usuario solicita recuperación**
   - En `/login`, hace click en "¿Olvidaste tu contraseña?"
   - Frontend envía `POST /api/auth/olvide-contrasena` con `{email}`

2. **Backend procesa la solicitud**
   - Busca usuario por email en la BD
   - **Si existe**: Genera token seguro con `secrets.token_urlsafe(32)` (32 bytes URL-safe)
   - Calcula hash SHA-256 del token: `hashlib.sha256(token.encode()).hexdigest()`
   - Guarda en tabla `recuperacion_contrasena`: `usuario_id`, `fecha_solicitud`, `token_hash`, `fecha_vencimiento` (24h), `usado=False`
   - Invalida tokens previos no usados del mismo usuario (actualiza `usado=True`)
   - Envía email (si SMTP configurado) con enlace: `FRONTEND_URL/reestablecer-contrasena?token=<token_plano>`
   - **Si NO existe**: Devuelve **200 OK** con mensaje genérico (no revela si el email existe por seguridad)

3. **Usuario recibe email y hace click**
   - Frontend lee parámetro `?token=` de la URL en `/reestablecer-contrasena`

4. **Usuario ingresa nueva contraseña**
   - Frontend envía `POST /api/auth/reestablecer-contrasena` con `{token, password, confirm_password}`

5. **Backend valida y actualiza**
   - Calcula SHA-256 del token entrante
   - Busca en BD por `token_hash` donde `usado=False`
   - Valida que no esté expirado (`fecha_vencimiento > now()`) ni usado
   - Actualiza password del usuario con `set_password()`
   - Marca token como `usado=True`
   - Responde 200 OK

6. **Usuario hace login** con nueva contraseña

### Consideraciones de seguridad:

- **Token nunca en claro en BD**: Solo se guarda el hash SHA-256. El token plano solo viaja en el email y URL.
- **Token en URL (query string)**: Estándar de la industria para password reset. Implicación: queda en logs del servidor, historial del navegador y referrers. Se mitiga con expiración corta (24h) y un solo uso.
- **Invalidación de tokens previos**: Al crear uno nuevo, los anteriores del mismo usuario se marcan como usados.
- **Expiración**: 24 horas por defecto (`expiracion_horas=24` en `crear_solicitud`).
- **Rate limiting implícito**: Solo un token activo por usuario a la vez.
- **Respuesta uniforme**: Siempre 200 OK en solicitud para no revelar existencia de emails.

### Tabla BD: `recuperacion_contrasena`

```sql
CREATE TABLE recuperacion_contrasena (
    id SERIAL PRIMARY KEY,
    usuario_id INT REFERENCES usuarios(id),
    fecha_solicitud TIMESTAMP NOT NULL DEFAULT NOW(),
    token_hash VARCHAR(64) UNIQUE NOT NULL,
    fecha_vencimiento TIMESTAMP NOT NULL,
    usado BOOLEAN DEFAULT FALSE
);
```

### Variables de entorno requeridas (.env)

```env
# Frontend URL para enlaces en emails
FRONTEND_URL=http://localhost:5173

# Email (ZohoMail)
SMTP_HOST=smtp.zoho.com
SMTP_PORT=587
SMTP_USER=tu-email@zoho.com
SMTP_PASSWORD=tu-password-de-app
FROM_EMAIL=tu-email@zoho.com
FROM_NAME=KeiBeauty
```

## Datos de Prueba (Seed)

El script `seed.py` crea:

- **1 Usuario Admin**: `admin@keibeauty.com` / `admin123` (rol: admin)
- **3 Marcas K-Beauty**: COSRX, Beauty of Joseon, Some By Mi
- **3 Categorías**: Limpieza, Hidratación, Tratamiento
- **5 Productos**: Limpiador COSRX, Esencia Snail 96, Dynasty Cream, Glow Serum, Miracle Toner

## Comandos Útiles

```bash
# Ver logs de la API
docker compose logs -f api

# Reiniciar solo la API
docker compose restart api

# Ejecutar comandos Flask en el contenedor
docker compose run --rm api flask db migrate -m "nombre_migracion"
docker compose run --rm api flask db upgrade
docker compose run --rm api python seed.py

# Acceder a shell del contenedor API
docker compose run --rm api bash

# Acceder a PostgreSQL
docker compose exec db psql -U postgres -d keibeauty_db

# Detener todo
docker compose down

# Detener y eliminar volúmenes (CUIDADO: borra datos BD)
docker compose down -v
```

## Producción

Para desplegar en producción:

1. **Cambiar variables de entorno** en `.env`:
   - `FLASK_ENV=production`
   - `SECRET_KEY` y `JWT_SECRET_KEY` seguras y únicas
   - `DATABASE_URL` apuntando a BD gestionada (RDS, Cloud SQL, etc.)
   - `CORS_ORIGINS` con dominios permitidos del frontend

2. **Usar Dockerfile multi-stage** (ya configurado):
   - Usuario sin privilegios (`appuser`)
   - Gunicorn con 4 workers y 2 threads
   - Imagen basada en Python slim

3. **Variables sensibles**: Nunca commitear `.env` real. Usar secrets manager (AWS Secrets Manager, HashiCorp Vault, Docker Secrets, etc.)

## Licencia

Proyecto privado - KeiBeauty