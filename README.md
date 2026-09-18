# KeiBeauty Backend — API REST

API REST del e-commerce **KeiBeauty** (nombre comercial en redes: **Kei Esencia**),
empresa guatemalteca fundada en 2021 dedicada a la comercialización e importación
de productos coreanos de belleza (K-Beauty): skincare y haircare.

Este backend gestiona el catálogo de productos, autenticación de clientes y
administradores (con 2FA por email), carrito persistido (autenticados e invitados),
pedidos con checkout invitado, favoritos, reseñas, notificaciones in-app, reportes
de ventas con exportación a Excel e inventario con control de stock en tiempo real.

Proyecto de Seminario de Sistemas 1 — Universidad de San Carlos de Guatemala,
Centro Universitario de Occidente (USAC-CUNOC). Actualmente en Fase 2.

## Stack tecnológico

| Tecnología | Versión | Uso |
|---|---|---|
| Python | 3.12+ | Lenguaje |
| Flask | 3.0.3 | Framework web (patrón Blueprint) |
| Flask-SQLAlchemy | 3.1.1 | ORM |
| Flask-Migrate (Alembic) | 4.0.5 | Migraciones de BD |
| Flask-JWT-Extended | 4.6.0 | Autenticación JWT (access + refresh + temporal 2FA) |
| Flask-CORS | 4.0.1 | CORS por entorno |
| Gunicorn | 22.0.0 | Servidor WSGI en producción |
| PostgreSQL | 16 | Base de datos relacional |
| psycopg2-binary | 2.9.9 | Driver PostgreSQL |
| imagekitio | 5.9.0 | Subida de imágenes (productos, marcas) |
| openpyxl | 3.1.5 | Exportación de reportes a Excel |
| python-dotenv | 1.0.1 | Variables de entorno |
| Docker + Docker Compose | — | Contenedores (API + PostgreSQL) |
| ZohoMail (SMTP) | — | Envío de correos (2FA, recuperación, pedidos) |

## Requisitos previos

- Python 3.11+ (recomendado 3.12)
- Docker + Docker Compose (opción recomendada), o PostgreSQL 16 local
- Git

> **Windows/WSL:** configurar `git config core.autocrlf true`. Se recomienda
> trabajar dentro de WSL2 con Docker Desktop y la integración WSL habilitada.

## Instalación en local

### Opción A — con Docker (recomendada)

```bash
git clone <url-del-repo> KeiBeauty
cd KeiBeauty

# 1. Copiar y completar variables de entorno
cp .env.example .env
# Editar .env (ver tabla de variables más abajo)

# 2. Levantar API + PostgreSQL (aplica migraciones automáticamente al arrancar)
docker compose up -d --build

# 3. Verificar contenedores
docker compose ps
docker compose logs --tail=50 api

# 4. Poblar datos de prueba
docker compose exec api python seed.py

# 5. Verificar que responde
curl -i http://localhost:5000/health
```

### Opción B — instalación manual (sin Docker)

```bash
git clone <url-del-repo> KeiBeauty
cd KeiBeauty

cp .env.example .env
# Editar .env con tu DATABASE_URL de PostgreSQL local

python3 -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate
pip install -r requirements.txt

# Crear la base de datos en PostgreSQL
createdb keibeauty_db           # o CREATE DATABASE keibeauty_db;

# Aplicar migraciones
flask db upgrade

# Poblar datos de prueba
python seed.py

# Iniciar servidor de desarrollo
flask run --port 5000
# En producción se usa Gunicorn (ver Dockerfile):
# gunicorn --bind 0.0.0.0:5000 --workers 4 --threads 2 --timeout 120 "app:create_app()"
```

## Variables de entorno

Copiar `.env.example` a `.env` y completar. Las variables que el código lee
realmente (vía `config.py` y `docker-compose.yml`) son:

| Variable | Obligatoria | Descripción | Ejemplo |
|---|---|---|---|
| `SECRET_KEY` | Sí (prod.) | Clave de sesiones Flask | `cambia-esto-en-produccion` |
| `JWT_SECRET_KEY` | Sí (prod.) | Clave de firma de tokens JWT | `otra-clave-segura` |
| `DATABASE_URL` | Sí | Cadena de conexión PostgreSQL | `postgresql://postgres:postgres@localhost:5432/keibeauty_db` |
| `FLASK_ENV` | No | Entorno (`development`/`production`) | `development` |
| `FLASK_APP` | No | App Flask para CLI | `app.py` |
| `CORS_ORIGINS` | No | Orígenes permitidos (coma-separados) | `http://localhost:5173,http://127.0.0.1:5173` |
| `FRONTEND_URL` | No | URL del frontend para enlaces en emails | `http://localhost:5173` |
| `SMTP_HOST` | No | Servidor SMTP (ZohoMail) | `smtp.zoho.com` |
| `SMTP_PORT` | No | Puerto SMTP | `587` |
| `SMTP_USER` | Sí* | Usuario SMTP (remitente) | `tienda@tudominio.com` |
| `SMTP_PASSWORD` | Sí* | Contraseña SMTP | `****` |
| `FROM_EMAIL` | No | Remitente (por defecto = `SMTP_USER`) | `tienda@tudominio.com` |
| `FROM_NAME` | No | Nombre del remitente | `KeiBeauty` |
| `IMAGEKIT_PRIVATE_KEY` | Sí* | Clave privada ImageKit (subida de imágenes) | `private_...` |
| `IMAGEKIT_PUBLIC_KEY` | Sí* | Clave pública ImageKit | `public_...` |
| `IMAGEKIT_URL_ENDPOINT` | Sí* | Endpoint ImageKit | `https://ik.imagekit.io/tu_cuenta` |

\* Obligatorias solo si se usa esa función: SMTP para correos (2FA, recuperación
de contraseña, confirmación de pedidos); ImageKit para subir imágenes de
productos/marcas/guías. Sin ellas, esas operaciones fallan con error 500
controlado y mensaje explicativo (los pedidos y el login NO se bloquean por
fallos de email).

> **Nota:** `.env.example` incluye además `MAIL_USERNAME`, `MAIL_PASSWORD` y
> `WHATSAPP_CHAT_URL`, que el backend actual **no lee** (el código usa
> `SMTP_USER`/`SMTP_PASSWORD`; la URL de WhatsApp vive en el frontend como
> `VITE_WHATSAPP_URL`). Están pendientes de limpieza en `.env.example`.

## Estructura del proyecto

```
KeiBeauty/
├── app.py                  # Factory create_app(): CORS, JWT, Blueprints, /health
├── config.py               # Config por entorno (dev/prod/testing) desde variables
├── requirements.txt        # Dependencias Python
├── seed.py                 # Datos de prueba (admin, marcas, categorías, productos)
├── .env.example            # Plantilla de variables de entorno
├── Dockerfile              # Multi-stage build (builder → runtime, usuario appuser)
├── docker-compose.yml      # Servicios api + db (PostgreSQL 16), migraciones al arrancar
├── migrations/versions/    # 15 migraciones Alembic (ver listado abajo)
├── models/                 # Modelos SQLAlchemy
│   ├── db.py               # Instancia SQLAlchemy
│   ├── usuario.py          # Usuario (nombre, email, password hasheada, rol, 2FA)
│   ├── marca.py            # Marca (nombre, descripcion, logo_url)
│   ├── categoria.py        # Categoria (nombre, descripcion)
│   ├── producto.py         # Producto (+ tamano, marca/categoria, imagenes, resenas)
│   ├── producto_imagen.py  # Galería de imágenes (es_principal, orden)
│   ├── producto_favorito.py# Favoritos (único por usuario+producto)
│   ├── producto_alerta.py  # Alertas "avísame" de stock por usuario+producto
│   ├── carrito.py          # Carrito + DetalleCarrito (usuario_id o guest_token)
│   ├── pedido.py           # Pedido + DetallePedido (snapshot precio_unitario/subtotal)
│   ├── codigo_2fa.py       # Códigos 2FA de 6 dígitos (hash, 5 min, 5 intentos)
│   ├── recuperacion_contrasena.py # Tokens SHA-256 de un solo uso (24 h)
│   ├── resena.py           # Reseña (calificacion 1-5, comentario)
│   ├── notificacion.py     # Notificación in-app (tipo, titulo, mensaje, datos JSON)
│   └── inventario_movimiento.py # Movimientos entrada/salida (+ costo_unitario)
├── routes/                 # Blueprints (un archivo por recurso)
│   ├── auth.py             # /api/auth/*
│   ├── products.py         # /api/products/*
│   ├── categorias.py       # /api/categorias/*
│   ├── marcas.py           # /api/marcas/*
│   ├── carrito.py          # /api/carrito/*
│   ├── pedidos.py          # /api/pedidos/*
│   ├── favoritos.py        # /api/favoritos/*
│   ├── resenas.py          # /api/resenas/*
│   ├── notificaciones.py   # /api/notificaciones/*
│   └── reportes.py         # /api/reportes/* (admin, JSON o Excel)
└── utils/
    ├── decorators.py       # @admin_required, @solo_en_autenticacion, etc.
    └── email.py            # Servicio SMTP (2FA, recuperación, pedidos)
```

## Endpoints de la API

Base URL local: `http://localhost:5000`. Todas las rutas JSON usan el prefijo
`/api/...`. Leyenda de auth: **—** = pública · **JWT** = access token
(`Authorization: Bearer <access_token>`) · **JWT-Admin** = JWT + rol `admin` ·
**JWT-temporal** = token de 10 min con claim `estado=en_autenticacion` (flujo 2FA) ·
**JWT-refresh** = refresh token.

### Sistema (`app.py`)

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| GET | `/health` | — | Salud del servicio (`{"status":"ok"}`) |
| GET | `/` | — | Nombre y versión de la API |

### Autenticación — `/api/auth`

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| POST | `/api/auth/registro` | — | Registro de cliente, devuelve tokens |
| POST | `/api/auth/login` | — | Login; si hay 2FA devuelve token temporal + envía código |
| POST | `/api/auth/verificar-2fa` | JWT-temporal | Valida código de 6 dígitos, devuelve tokens reales |
| POST | `/api/auth/reenviar-codigo-2fa` | JWT-temporal | Reenvía código (rate limit 60 s) |
| POST | `/api/auth/cancelar-login` | JWT-temporal | Invalida códigos pendientes del login en curso |
| POST | `/api/auth/activar-2fa` | JWT | Activa 2FA del usuario autenticado |
| POST | `/api/auth/desactivar-2fa` | JWT | Desactiva 2FA e invalida códigos pendientes |
| GET | `/api/auth/perfil` | JWT | Perfil del usuario autenticado |
| POST | `/api/auth/refresh` | JWT-refresh | Renueva el access token |
| POST | `/api/auth/olvide-contrasena` | — | Envía email con enlace de recuperación (siempre 200) |
| POST | `/api/auth/reestablecer-contrasena` | — | Restablece contraseña con token de un solo uso |

#### Contratos JSON — autenticación

**POST `/api/auth/registro`** — request (obligatorios: `nombre`, `email`,
`password`, `direccion_envio`; opcional: `telefono`):

```json
{
  "nombre": "María López",
  "email": "maria@ejemplo.com",
  "password": "secreta123",
  "telefono": "50255556666",
  "direccion_envio": "Zona 1, Xela"
}
```

Response `201`:

```json
{
  "mensaje": "Usuario registrado exitosamente.",
  "usuario": {
    "id": 2,
    "nombre": "María López",
    "email": "maria@ejemplo.com",
    "telefono": "50255556666",
    "direccion_envio": "Zona 1, Xela",
    "rol": "cliente",
    "two_factor_enabled": false,
    "fecha_registro": "2026-09-01T10:00:00"
  },
  "access_token": "<jwt-24h>",
  "refresh_token": "<jwt-30d>"
}
```

Códigos: `201` creado · `400` campos faltantes o email duplicado.

**POST `/api/auth/login`** — request:

```json
{ "email": "maria@ejemplo.com", "password": "secreta123" }
```

Sin 2FA → response `200` igual al de registro (`mensaje: "Login exitoso."`).
Con 2FA activado → response `200` (código enviado al email):

```json
{
  "data": {
    "requiere_2fa": true,
    "email": "maria@ejemplo.com",
    "token_temporal": "<jwt-10min>"
  },
  "message": "Código enviado a tu correo"
}
```

Códigos: `200` · `400` campos faltantes · `401` credenciales inválidas.

**POST `/api/auth/verificar-2fa`** (header `Authorization: Bearer <token_temporal>`)
— request:

```json
{ "codigo": "482913" }
```

Response `200`: igual al login sin 2FA (`access_token`, `refresh_token`, `usuario`).
Códigos: `200` · `400` código inválido/expirado o demasiados intentos · `404` usuario no existe.

**POST `/api/auth/reenviar-codigo-2fa`** (JWT-temporal, sin body) → `200`
`{"data": null, "message": "Código reenviado"}` · `429` si pasaron < 60 s.

**POST `/api/auth/cancelar-login`** (JWT-temporal, sin body) → `200`
`{"message": "Login cancelado. El código pendiente ha sido invalidado."}`.

**POST `/api/auth/activar-2fa`** (JWT, sin body) → `200`
`{"data": {"two_factor_enabled": true}, "message": "2FA activado exitosamente"}`.

**POST `/api/auth/desactivar-2fa`** (JWT, sin body) → `200`
`{"data": {"two_factor_enabled": false}, "message": "2FA desactivado exitosamente"}`.

**GET `/api/auth/perfil`** (JWT) → `200` `{"usuario": {...mismo objeto de registro...}}` ·
`401` sin token · `404` usuario no existe.

**POST `/api/auth/refresh`** (header `Authorization: Bearer <refresh_token>`) → `200`
`{"access_token": "<nuevo-jwt-24h>"}`.

**POST `/api/auth/olvide-contrasena`** — request `{"email": "maria@ejemplo.com"}` →
siempre `200` `{"data": null, "message": "Si el email existe, recibirás instrucciones..."}`.

**POST `/api/auth/reestablecer-contrasena`** — request:

```json
{ "token": "<token-del-email>", "password": "nueva123", "confirm_password": "nueva123" }
```

Response `200` `{"data": null, "message": "Contraseña restablecida exitosamente..."}`.
Códigos: `200` · `400` token inválido/expirado/usado, claves distintas o < 6 caracteres.

### Productos — `/api/products`

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| GET | `/api/products` | — | Lista productos (query: `categoria`, `marca`, `buscar`, `con_favorito`, `estado`) |
| GET | `/api/products/<id>` | — | Detalle (clientes solo `activo`; admin ve todos) |
| GET | `/api/products/categorias` | — | `[{id, nombre}]` para filtros |
| GET | `/api/products/marcas` | — | `[{id, nombre, ...}]` para filtros |
| POST | `/api/products` | JWT-Admin | Crear (JSON o `multipart/form-data` con `archivo`) |
| PUT | `/api/products/<id>` | JWT-Admin | Editar (JSON o multipart) |
| DELETE | `/api/products/<id>` | JWT-Admin | Eliminar |
| POST | `/api/products/<id>/imagen` | JWT-Admin | Subir imagen principal (`multipart`, campo `archivo`) |
| GET | `/api/products/<id>/imagenes` | — | Galería del producto |
| POST | `/api/products/<id>/imagenes` | JWT-Admin | Subir galería (`multipart`, campo `archivos` múltiple) |
| PUT | `/api/products/<id>/imagenes/<img>/principal` | JWT-Admin | Marcar imagen principal |
| DELETE | `/api/products/<id>/imagenes/<img>` | JWT-Admin | Eliminar imagen de galería |
| POST | `/api/products/<id>/inventario` | JWT-Admin | Ajuste `{tipo: entrada\|salida, cantidad, costo_unitario?}` |
| GET | `/api/products/admin-test` | JWT-Admin | Diagnóstico de rol admin |

Query params de `GET /api/products`: `categoria=<id>`, `marca=<id>`,
`buscar=<texto en nombre>`, `con_favorito=1` (agrega `es_favorito` si hay JWT),
`estado=activo|inactivo|agotado` (solo admin; sin estado el admin ve todos;
clientes siempre solo `activo`).

#### Contratos JSON — productos

**GET `/api/products?marca=1&buscar=snail&con_favorito=1`** → `200`:

```json
{
  "data": [
    {
      "id": 2,
      "nombre": "Advanced Snail 96 Mucin Power Essence",
      "descripcion": "Esencia con 96% de mucina...",
      "ingredientes_clave": "Mucina de caracol (96%), ...",
      "tipo_piel": "Todo tipo de piel",
      "tamano": "100ml",
      "precio": 22.5,
      "stock": 40,
      "imagen_url": "https://...",
      "imagenes": [{ "id": 1, "imagen_url": "https://...", "es_principal": true, "orden": 0 }],
      "estado": "activo",
      "marca_id": 1,
      "categoria_id": 3,
      "marca_nombre": "COSRX",
      "marca_logo_url": "https://...",
      "categoria_nombre": "Tratamiento",
      "fecha_creacion": "2026-09-01T10:00:00",
      "es_favorito": true
    }
  ],
  "message": "Productos obtenidos exitosamente."
}
```

**POST `/api/products`** (admin, JSON o multipart) — campos obligatorios:
`nombre`, `precio` (> 0), `stock` (≥ 0), `marca_id`, `categoria_id`. Opcionales:
`descripcion`, `ingredientes_clave`, `tipo_piel`, `tamano` (máx. 255),
`estado`, `imagen_url` o `archivo` (jpeg/png/gif/webp, se sube a ImageKit
carpeta `/productos`):

```json
{
  "nombre": "Green Tea Seed Serum",
  "descripcion": "Sérum hidratante de té verde",
  "precio": 24.99,
  "stock": 20,
  "marca_id": 1,
  "categoria_id": 3,
  "tamano": "80ml",
  "tipo_piel": "Mixta, grasa"
}
```

Response `201` `{"data": {<producto>}, "message": "Producto creado exitosamente."}`.
Códigos: `201` · `400` validación · `404` marca/categoría inexistente ·
`401/403` sin auth o sin rol admin · `500` ImageKit no configurado.

**POST `/api/products/<id>/inventario`** (admin) — request:

```json
{ "tipo": "entrada", "cantidad": 10, "costo_unitario": 12.50 }
```

(`costo_unitario` solo aplica a `entrada`; `salida` descuenta stock.)
Response `200` con el producto actualizado. Códigos: `200` · `400` tipo/cantidad
inválidos o stock insuficiente.

### Categorías — `/api/categorias`

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| GET | `/api/categorias` | — | Lista ordenada por nombre |
| POST | `/api/categorias` | JWT-Admin | Crear `{"nombre", "descripcion?"}` |
| PUT | `/api/categorias/<id>` | JWT-Admin | Editar |
| DELETE | `/api/categorias/<id>` | JWT-Admin | Eliminar |

Objeto categoría: `{"id": 1, "nombre": "Limpieza", "descripcion": "..."}`.
Códigos: `200/201` · `400` nombre vacío/duplicado · `404` no existe.

### Marcas — `/api/marcas`

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| GET | `/api/marcas` | — | Lista de marcas |
| POST | `/api/marcas` | JWT-Admin | Crear (JSON o multipart con `archivo` de logo → ImageKit `/marcas`) |
| PUT | `/api/marcas/<id>` | JWT-Admin | Editar |
| DELETE | `/api/marcas/<id>` | JWT-Admin | Eliminar |

Request crear: `{"nombre": "Tocobo", "descripcion": "...", "logo_url": "https://..."}`.
Códigos: `201` · `400` nombre vacío/duplicado o tipo de imagen no permitido.

### Carrito — `/api/carrito`

El carrito se resuelve por JWT si hay sesión, o por header `X-Guest-Token` para
invitados (el backend crea el token de invitado y el frontend lo guarda en
`localStorage`).

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| GET | `/api/carrito` | JWT o guest | Obtiene carrito con detalles y total |
| POST | `/api/carrito/items` | JWT o guest | Agrega `{"producto_id", "cantidad?"}` (valida stock) |
| PUT | `/api/carrito/items/<item_id>` | JWT o guest | Cambia cantidad (valida stock) |
| DELETE | `/api/carrito/items/<item_id>` | JWT o guest | Quita un ítem |
| DELETE | `/api/carrito` | JWT o guest | Vacía el carrito |

**POST `/api/carrito/items`** — request `{"producto_id": 2, "cantidad": 1}` →
`200/201` `{"data": {<carrito con detalles>}, "message": "..."}`.
Códigos: `200/201` · `400` producto inactivo o stock insuficiente · `404` producto no existe.

Objeto carrito:

```json
{
  "id": 1,
  "usuario_id": 2,
  "guest_token": null,
  "fecha_creacion": "2026-09-01T10:00:00",
  "fecha_actualizacion": "2026-09-01T10:05:00",
  "detalles": [
    { "id": 5, "producto_id": 2, "cantidad": 1, "subtotal": 22.5, "producto": { "..." } }
  ]
}
```

### Pedidos — `/api/pedidos`

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| POST | `/api/pedidos` | — (JWT opcional) | Checkout: autenticado usa su carrito; invitado usa carrito guest o `items` |
| GET | `/api/pedidos` | JWT | Lista propia (cliente, `?page&per_page&estado`) o todos (admin) |
| GET | `/api/pedidos/<id>` | JWT o guest | Detalle (dueño, admin, o invitado con `guest_token`/`email_contacto`) |
| PATCH | `/api/pedidos/<id>/estado` | JWT-Admin | Cambia estado + notifica (in-app y email) |
| PUT/POST | `/api/pedidos/<id>/guia` | JWT-Admin | Sube imagen de guía (`multipart`, campo `archivo`) |

Estados válidos: `pendiente`, `confirmado`, `enviado`, `entregado`, `cancelado`.
Al crear, el stock se descuenta automáticamente; si llega a 0 el producto pasa a
`agotado`. Invitados reciben el pedido y lo consultan con su `guest_token`.

#### Contratos JSON — pedidos

**POST `/api/pedidos`** (autenticado; el carrito se toma del backend) — request:

```json
{ "direccion_envio": "12 Av. Zona 3, Xela" }
```

**POST `/api/pedidos`** (invitado) — request:

```json
{
  "direccion_envio": "12 Av. Zona 3, Xela",
  "email_contacto": "invitado@ejemplo.com",
  "telefono_contacto": "50255556666",
  "items": [{ "producto_id": 2, "cantidad": 1 }]
}
```

(`items` solo se usa si el invitado no tiene carrito guest asociado.)
Response `201` `{"data": {<pedido con detalles>}, "message": "Pedido creado exitosamente."}`.
Códigos: `201` · `400` dirección/email/teléfono faltantes, carrito vacío o stock
insuficiente.

Objeto pedido:

```json
{
  "id": 10,
  "usuario_id": 2,
  "monto_total": 45.0,
  "estado": "pendiente",
  "direccion_envio": "12 Av. Zona 3, Xela",
  "email_contacto": "maria@ejemplo.com",
  "telefono_contacto": "50255556666",
  "fecha_pedido": "2026-09-01T11:00:00",
  "fecha_actualizacion": "2026-09-01T11:00:00",
  "url_guia": null,
  "detalles": [
    {
      "id": 20, "pedido_id": 10, "producto_id": 2,
      "precio_unitario": 22.5, "cantidad": 2,
      "nombre_producto": "Advanced Snail 96...",
      "subtotal": 45.0
    }
  ]
}
```

**PATCH `/api/pedidos/<id>/estado`** (admin) — request `{"estado": "enviado"}` →
`200` con el pedido actualizado. Códigos: `200` · `400` estado inválido · `404` no existe.

### Favoritos — `/api/favoritos` (JWT)

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/favoritos` | Lista de favoritos del usuario |
| POST | `/api/favoritos/<producto_id>` | Agrega a favoritos |
| DELETE | `/api/favoritos/<producto_id>` | Quita de favoritos |

### Reseñas — `/api/resenas`

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| GET | `/api/resenas?producto=<id>` | — | Públicas por producto (+ `promedio` y `total`) |
| GET | `/api/resenas` | JWT-Admin | Todas las reseñas |
| POST | `/api/resenas` | JWT | Crear (solo si compró el producto, una por usuario+producto) |
| PUT | `/api/resenas/<id>` | JWT-Admin | Editar calificación/comentario |
| DELETE | `/api/resenas/<id>` | JWT-Admin | Eliminar |

**POST `/api/resenas`** — request `{"producto_id": 2, "calificacion": 5, "comentario": "Me encantó"}`.
`calificacion` entero 1–5. Response `201`. Códigos: `201` · `400` duplicada o rango
inválido · `403` no compró el producto · `404` producto no existe.

### Notificaciones — `/api/notificaciones` (JWT)

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/notificaciones` | Últimas 50 + contador `no_leidas` |
| PUT | `/api/notificaciones/<id>/leida` | Marca una como leída |
| PUT | `/api/notificaciones/leer-todas` | Marca todas como leídas |
| GET | `/api/notificaciones/producto/<id>/alerta` | Consulta si hay alerta "avísame" de stock |
| POST | `/api/notificaciones/producto/<id>/alerta` | Crea alerta de stock (una por usuario+producto) |
| DELETE | `/api/notificaciones/producto/<id>/alerta` | Elimina la alerta |

Tipos de notificación (`tipo`): `pedido_estado`, `pedido_guia`, `producto_stock`.
Objeto: `{"id", "usuario_id", "tipo", "titulo", "mensaje", "leido", "datos": {"pedido_id"...}, "fecha_creacion"}`.

### Reportes — `/api/reportes` (JWT-Admin)

Todos aceptan `desde=YYYY-MM-DD`, `hasta=YYYY-MM-DD` y `excel=1` (o
`formato=excel`) para descargar `.xlsx` en lugar de JSON.

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/reportes/ventas-totales` | Total de ventas y nº de pedidos (excluye cancelados) |
| GET | `/api/reportes/ventas-por-mes` | Ventas agrupadas por mes |
| GET | `/api/reportes/ventas-por-periodo` | Pedidos entre `desde` y `hasta` (ambos obligatorios) |
| GET | `/api/reportes/ganancias` | Ventas vs. costos (costo de movimientos `entrada`) |
| GET | `/api/reportes/productos-mas-vendidos` | Top productos (`limit`, por defecto 10) |
| GET | `/api/reportes/clientes-top` | Top clientes (`limit`, por defecto 10) |

Ejemplo: `GET /api/reportes/ventas-totales?desde=2026-09-01&hasta=2026-09-30` →
`200` `{"data": {"total_ventas": 1250.0, "total_pedidos": 18, ...}}`.
Con `&excel=1` → descarga `ventas_totales.xlsx` (`Content-Type:
application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`).

> **Pendiente:** exportación a PDF (solo Excel implementado).

## Migraciones

```bash
# Aplicar migraciones pendientes
flask db upgrade
# En Docker:
docker compose exec api flask db upgrade

# Ver migración actual
flask db current

# Crear una nueva migración tras cambiar models/
flask db migrate -m "descripcion del cambio"

# Revertir la última
flask db downgrade
```

Migraciones existentes en `migrations/versions/` (orden de creación):

| Archivo | Contenido |
|---|---|
| `1946dc26b0bd_initial_migration.py` | Migración inicial |
| `19c2960f0082_add_recuperacion_contrasena_table.py` | Tabla recuperación de contraseña |
| `2fa_migracion_2026.py` | 2FA (códigos + flag en usuario) |
| `2026_guest_token_carritos.py` | `guest_token` en carritos |
| `2026_email_telefono_pedido.py` | Email/teléfono de contacto en pedidos |
| `2026_nombre_pedido.py` + `188f4f333d85_fusionar_heads_...` | Nombre de pedido + fusión de heads |
| `2026_subtotal_detalle_pedidos.py` | Snapshot `precio_unitario` + `subtotal` |
| `2026_usuario_id_nullable_pedido.py` | Pedidos de invitados (`usuario_id` nullable) |
| `2026_producto_imagenes_galeria.py` | Galería de imágenes |
| `2026_tamano_producto.py` | Columna `tamano` |
| `2026_url_guia_pedido.py` | `url_guia` en pedidos |
| `2026_inventario_movimientos.py` + `2026_inventario_costo_unitario.py` | Movimientos + costo |
| `2026_notificaciones_alerta.py` | Notificaciones y alertas de stock |

## Seeders

`seed.py` crea datos de prueba si no existe el admin. Correr con:

```bash
python seed.py
# En Docker:
docker compose exec api python seed.py
```

Datos que crea:

| Dato | Detalle |
|---|---|
| Admin | `admin@keibeauty.com` / `admin123` (rol `admin`) |
| Marcas (3) | COSRX, Beauty of Joseon, Some By Mi |
| Categorías (3) | Limpieza, Hidratación, Tratamiento |
| Productos (5) | Limpiador COSRX, Snail Essence, Dynasty Cream, Glow Serum, Miracle Toner |

> **Nota:** el seed es mínimo (5 productos, sin `tamano`, sin cliente de prueba,
> sin pedidos). Para verificación rica conviene crear un cliente y pedidos desde
> el frontend o la API.

## Testing

No hay suite de tests automatizados en el backend (pendiente). Verificación
actual: `curl` a `/health` y `/api/products`, más pruebas manuales del flujo
(login → carrito → checkout) documentadas en `REPORTE-SESION-FINAL.md`.

## GitFlow

Ramas: `main` (producción, estable) · `develop` (integración) ·
`feature/*` (nuevas funcionalidades) · `hotfix/*` (emergencias en producción).

Reglas obligatorias:

- Rama `feature/*` siempre desde `develop`. Mensajes de commit simples en español.
- Merge a `develop` con `--no-ff`. Push de la rama y de `develop`. **No borrar** la rama.
- Prohibido: rebase, force push, tocar `main`, borrar tags (`funcional-1`…`release-2`).
- Si algo se rompe: parar y documentar en `REPORTE-SESION-FINAL.md`.
- En Windows: `git config core.autocrlf true`.

## Notas de seguridad

- Contraseñas con hash `pbkdf2` (Werkzeug, `generate_password_hash`); nunca en claro.
- Tokens de recuperación hasheados con **SHA-256**, validez 24 h y un solo uso.
- Códigos 2FA de 6 dígitos hasheados, válidos 5 min, máx. 5 intentos fallidos y
  reenvío con rate limit de 60 s. Respuestas genéricas para no revelar emails.
- JWT: access 24 h + refresh 30 d + temporal 2FA de 10 min con claim
  `estado=en_autenticacion` (decoradores `@solo_en_autenticacion` /
  `@rechazar_en_autenticacion` aíslan el flujo 2FA del resto).
- CORS configurable por entorno (`CORS_ORIGINS` + regex localhost); en
  producción restringir orígenes y servir por HTTPS.
- Secretos solo por variables de entorno (`.env` no versionado); ImageKit y SMTP
  fuera del código.
- Validación estricta de stock antes de confirmar compras; descuento atómico en
  la transacción del pedido.

## Troubleshooting

| Problema | Causa probable / solución |
|---|---|
| `flask db upgrade` falla con "relation already exists" | La BD ya tiene tablas sin Alembic: usar `flask db stamp head` solo si el esquema coincide, o recrear la BD. |
| `connection refused` a PostgreSQL | Verificar `DATABASE_URL` (en Docker el host es `db`, no `localhost`) y que el contenedor `db` esté `healthy`. |
| CORS bloquea al frontend | Agregar el origen a `CORS_ORIGINS` en `.env` y reiniciar (`docker compose restart api`). |
| Emails no llegan | Revisar `SMTP_USER`/`SMTP_PASSWORD` (ZohoMail usa contraseña de aplicación). Nota: `.env.example` aún menciona `MAIL_USERNAME`/`MAIL_PASSWORD`, que el código **no** usa. |
| Subida de imágenes → 500 "ImageKit no disponible" | Faltan `IMAGEKIT_*` en `.env`; sin ellas solo se puede usar `imagen_url` directa. |
| `seed.py` dice "Datos de prueba ya existen" | Ya hay admin; para reseedear borrar volúmenes: `docker compose down -v` (¡borra toda la BD!). |
| Puerto 5000 ocupado | Cambiar mapeo en `docker-compose.yml` (`"5001:5000"`) o detener el proceso local. |
| `permission denied` en Docker (Linux) | Usuario fuera del grupo docker: `sudo usermod -aG docker $USER` y reiniciar sesión. |
