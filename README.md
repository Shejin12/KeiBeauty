# KeiBeauty Backend — API REST

API REST del e-commerce **KeiBeauty** (nombre comercial en redes: **Kei Esencia**),
empresa guatemalteca fundada en 2021 dedicada a la comercialización e importación
de productos coreanos de belleza (K-Beauty): skincare y haircare.

Este backend gestiona el catálogo de productos, autenticación de clientes y
administradores (con 2FA por email), carrito persistido (autenticados e invitados),
pedidos con checkout invitado, favoritos, reseñas, notificaciones in-app, reportes
de ventas con exportación a Excel e inventario con control de stock en tiempo real.
Además sirve el build del frontend (`STATIC_DIR`) para desplegar tienda y API en
una sola URL.

Proyecto de Seminario de Sistemas 1 — Universidad de San Carlos de Guatemala,
Centro Universitario de Occidente (USAC-CUNOC). Fase 2.

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
| ZohoMail (SMTP) | — | Correos operativos (2FA, recuperación, pedidos) |

## Requisitos previos

- Python 3.11+ (recomendado 3.12)
- Docker + Docker Compose (opción recomendada), o PostgreSQL 16 local
- Git

> **Windows/WSL:** configurar `git config core.autocrlf true`. Se recomienda
> trabajar dentro de WSL2 con Docker Desktop y la integración WSL habilitada.

## Instalación en local

```bash
git clone git@github.com:Shejin12/KeiBeauty.git KeiBeauty
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

Instalación manual (sin Docker):

```bash
git clone git@github.com:Shejin12/KeiBeauty.git KeiBeauty
cd KeiBeauty

cp .env.example .env
# Editar .env con tu DATABASE_URL de PostgreSQL local

python3 -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate
pip install -r requirements.txt

createdb keibeauty_db           # o CREATE DATABASE keibeauty_db;
flask db upgrade
python seed.py
flask run --port 5000
# Producción (ver Dockerfile):
# gunicorn --bind 0.0.0.0:5000 --workers 4 --threads 2 --timeout 120 "app:create_app()"
```

## Variables de entorno

Copiar `.env.example` a `.env` y completar. El código lee (vía `config.py` y
`docker-compose.yml`):

| Variable | Obligatoria | Descripción | Ejemplo |
|---|---|---|---|
| `SECRET_KEY` | Sí (prod.) | Clave de sesiones Flask | `cambia-esto-en-produccion` |
| `JWT_SECRET_KEY` | Sí (prod.) | Clave de firma de tokens JWT | `otra-clave-segura` |
| `DATABASE_URL` | Sí | Conexión PostgreSQL | `postgresql://postgres:postgres@localhost:5432/keibeauty_db` |
| `FLASK_ENV` | No | Entorno (`development`/`production`) | `development` |
| `FLASK_APP` | No | App Flask para CLI | `app.py` |
| `CORS_ORIGINS` | No | Orígenes permitidos (coma-separados) | `http://localhost:5173,http://127.0.0.1:5173` |
| `CORS_ORIGINS_REGEX_EXTRA` | No | Regex extra de orígenes (ej. ngrok con URL cambiante) | `https://.*\.ngrok-free\.app` |
| `FRONTEND_URL` | No | URL del frontend para enlaces en emails | `http://localhost:5173` |
| `STATIC_DIR` | No | Directorio con el build del frontend para servir la SPA; vacío = solo JSON | `/frontend-dist` |
| `SMTP_HOST` | Sí | Servidor SMTP (ZohoMail) | `smtp.zoho.com` |
| `SMTP_PORT` | Sí | Puerto SMTP | `587` |
| `SMTP_USER` | Sí | Cuenta Zoho completa (remitente) | `tienda@tudominio.com` |
| `SMTP_PASSWORD` | Sí | Contraseña de aplicación de Zoho | `****` |
| `FROM_EMAIL` | No | Remitente (por defecto = `SMTP_USER`) | `tienda@tudominio.com` |
| `FROM_NAME` | No | Nombre del remitente | `KeiBeauty` |
| `IMAGEKIT_PRIVATE_KEY` | Sí* | Clave privada ImageKit (subida de imágenes) | `private_...` |
| `IMAGEKIT_PUBLIC_KEY` | Sí* | Clave pública ImageKit | `public_...` |
| `IMAGEKIT_URL_ENDPOINT` | Sí* | Endpoint ImageKit | `https://ik.imagekit.io/tu_cuenta` |

\* Solo para subir imágenes (productos, marcas, guías). Sin ellas se usa
`imagen_url` directa; la subida devuelve 500 controlado con mensaje explicativo.
Los pedidos y el login no se bloquean por fallos de email.

Correo (ZohoMail, operativo): `SMTP_USER` es la cuenta que inicia sesión y
`FROM_EMAIL` el remitente. Zoho rechaza (`553 Sender is not allowed to relay
emails`) cualquier remitente distinto de la cuenta autenticada; por eso
`FROM_EMAIL` es igual a `SMTP_USER` (o se deja vacío). `SMTP_PASSWORD` es una
contraseña de aplicación generada en el panel de Zoho, no la contraseña normal.

## Estructura del proyecto

```
KeiBeauty/
├── app.py                  # Factory create_app(): CORS, JWT, Blueprints, /health, SPA
├── config.py               # Config por entorno (dev/prod/testing) desde variables
├── requirements.txt        # Dependencias Python
├── seed.py                 # Datos de prueba (admin, marcas, categorías, productos)
├── .env.example            # Plantilla de variables de entorno
├── Dockerfile              # Multi-stage build (builder → runtime, usuario appuser)
├── docker-compose.yml      # api + db; monta ../KeiBeauty-frontend/dist en /frontend-dist
├── migrations/versions/    # 15 migraciones Alembic
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

Base URL local: `http://localhost:5000`. Rutas JSON bajo `/api/...`. Auth:
**—** = pública · **JWT** = access token · **JWT-Admin** = JWT + rol `admin` ·
**JWT-temporal** = token 2FA de 10 min · **JWT-refresh** = refresh token.

### Sistema

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| GET | `/health` | — | Salud (`{"status":"ok"}`) |
| GET | `/` | — | `index.html` de la tienda si `STATIC_DIR` está activo; si no, JSON informativo |

### Autenticación — `/api/auth`

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| POST | `/api/auth/registro` | — | Registro de cliente, devuelve tokens |
| POST | `/api/auth/login` | — | Login; con 2FA devuelve token temporal + envía código |
| POST | `/api/auth/verificar-2fa` | JWT-temporal | Valida código de 6 dígitos, devuelve tokens reales |
| POST | `/api/auth/reenviar-codigo-2fa` | JWT-temporal | Reenvía código (rate limit 60 s) |
| POST | `/api/auth/cancelar-login` | JWT-temporal | Invalida códigos pendientes del login en curso |
| POST | `/api/auth/activar-2fa` | JWT | Activa 2FA del usuario autenticado |
| POST | `/api/auth/desactivar-2fa` | JWT | Desactiva 2FA e invalida códigos pendientes |
| GET | `/api/auth/perfil` | JWT | Perfil del usuario autenticado |
| POST | `/api/auth/refresh` | JWT-refresh | Renueva el access token |
| POST | `/api/auth/olvide-contrasena` | — | Envía email de recuperación (siempre 200) |
| POST | `/api/auth/reestablecer-contrasena` | — | Restablece contraseña con token de un solo uso |

#### Contratos JSON — autenticación

**POST `/api/auth/registro`** (obligatorios: `nombre`, `email`, `password`,
`direccion_envio`; opcional: `telefono`):

```json
{ "nombre": "María López", 
  "email": "maria@ejemplo.com", 
  "password": "secreta123",
  "telefono": "50255556666", 
  "direccion_envio": "Zona 1, Xela" 
}
```

Response `201`:

```json
{ "mensaje": "Usuario registrado exitosamente.",
  "usuario": { 
                "id": 2, 
                "nombre": "María López", 
                "email": "maria@ejemplo.com",
                "telefono": "50255556666", 
                "direccion_envio": "Zona 1, Xela",
                "rol": "cliente", 
                "two_factor_enabled": true,
                "fecha_registro": "2026-09-01T10:00:00" 
              },
  "access_token": "<jwt-24h>", 
  "refresh_token": "<jwt-30d>" 
}
```

Códigos: `201` · `400` campos faltantes o email duplicado.

**POST `/api/auth/login`**: `{ "email": "...", "password": "..." }`.
Sin 2FA → `200` con la misma forma del registro (`"Login exitoso."`).
Con 2FA → `200`:

```json
{ "data": { 
            "requiere_2fa": true, 
            "email": "maria@ejemplo.com",
            "token_temporal": "<jwt-10min>" 
          },
  "message": "Código enviado a tu correo" 
}
```

Códigos: `200` · `400` campos faltantes · `401` credenciales inválidas.

**POST `/api/auth/verificar-2fa`** (`Authorization: Bearer <token_temporal>`):
`{ "codigo": "482913" }` → `200` con tokens reales.
Códigos: `200` · `400` código inválido/expirado o demasiados intentos · `404`.

**POST `/api/auth/reenviar-codigo-2fa`** (JWT-temporal, sin body) → `200`
`{"data": null, "message": "Código reenviado"}` · `429` si pasaron < 60 s.

**POST `/api/auth/cancelar-login`** (JWT-temporal) → `200` con mensaje de
cancelación. **POST `/api/auth/activar-2fa`** (JWT) → `200`
`{"data": {"two_factor_enabled": true}, ...}`.
**POST `/api/auth/desactivar-2fa`** (JWT) → `200` con `false`.

**GET `/api/auth/perfil`** (JWT) → `200` `{"usuario": {...}}` · `401` · `404`.
**POST `/api/auth/refresh`** (refresh token) → `200` `{"access_token": "..."}`.

**POST `/api/auth/olvide-contrasena`**: `{"email": "..."}` → siempre `200`.
**POST `/api/auth/reestablecer-contrasena`**:
`{"token": "<del-email>", "password": "nueva123", "confirm_password": "nueva123"}`
→ `200`. Códigos: `400` token inválido/expirado/usado, claves distintas o
< 6 caracteres.

### Productos — `/api/products`

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| GET | `/api/products` | — | Lista (query: `categoria`, `marca`, `buscar`, `con_favorito`, `estado`) |
| GET | `/api/products/<id>` | — | Detalle (clientes solo `activo`; admin todos) |
| GET | `/api/products/categorias` | — | `[{id, nombre}]` |
| GET | `/api/products/marcas` | — | `[{id, nombre, ...}]` |
| POST | `/api/products` | JWT-Admin | Crear (JSON o multipart con `archivo`) |
| PUT | `/api/products/<id>` | JWT-Admin | Editar (JSON o multipart) |
| DELETE | `/api/products/<id>` | JWT-Admin | Eliminar |
| POST | `/api/products/<id>/imagen` | JWT-Admin | Imagen principal (`multipart`, `archivo`) |
| GET | `/api/products/<id>/imagenes` | — | Galería |
| POST | `/api/products/<id>/imagenes` | JWT-Admin | Galería (`multipart`, `archivos` múltiple) |
| PUT | `/api/products/<id>/imagenes/<img>/principal` | JWT-Admin | Marcar principal |
| DELETE | `/api/products/<id>/imagenes/<img>` | JWT-Admin | Eliminar de galería |
| POST | `/api/products/<id>/inventario` | JWT-Admin | `{tipo: entrada\|salida, cantidad, costo_unitario?}` |
| GET | `/api/products/admin-test` | JWT-Admin | Diagnóstico de rol admin |

Query `GET /api/products`: `categoria=<id>`, `marca=<id>`, `buscar=<texto en
nombre, literal: `%` y `_` se escapan>`, `con_favorito=1` (agrega `es_favorito`
con JWT), `estado` (solo admin; clientes siempre solo `activo`).

**POST `/api/products`** (admin): obligatorios `nombre`, `precio` (> 0),
`stock` (≥ 0), `marca_id`, `categoria_id`; opcionales `descripcion`,
`ingredientes_clave`, `tipo_piel`, `tamano` (máx. 255), `estado`, `imagen_url` o
`archivo` (jpeg/png/gif/webp → ImageKit `/productos`). Response `201` con el
producto. Códigos: `201` · `400` · `404` marca/categoría · `401/403`.

Objeto producto (`to_dict` + `es_favorito` opcional):

```json
{ "id": 2, 
  "nombre": "Advanced Snail 96...", 
  "descripcion": "...",
  "ingredientes_clave": "...", 
  "tipo_piel": "Todo tipo de piel", 
  "tamano": "100ml",
  "precio": 22.5, 
  "stock": 40, 
  "imagen_url": "https://...",
  "imagenes": [{ "id": 1, "imagen_url": "https://...", "es_principal": true, "orden": 0 }],
  "estado": "activo", 
  "marca_id": 1, 
  "marca_nombre": "COSRX",
  "categoria_id": 3, 
  "categoria_nombre": "Tratamiento",
  "fecha_creacion": "2026-09-01T10:00:00", 
  "es_favorito": true 
}
```

**POST `/api/products/<id>/inventario`** (admin):
`{"tipo": "entrada", "cantidad": 10, "costo_unitario": 12.50}`
(`costo_unitario` solo en `entrada`). → `200` con el producto.

### Categorías — `/api/categorias`

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| GET | `/api/categorias` | — | Lista ordenada |
| POST | `/api/categorias` | JWT-Admin | `{"nombre", "descripcion?"}` → `201` |
| PUT | `/api/categorias/<id>` | JWT-Admin | Editar |
| DELETE | `/api/categorias/<id>` | JWT-Admin | Eliminar |

Códigos: `200/201` · `400` nombre vacío/duplicado · `404`.

### Marcas — `/api/marcas`

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| GET | `/api/marcas` | — | Lista |
| POST | `/api/marcas` | JWT-Admin | JSON o multipart (`archivo` → ImageKit `/marcas`) → `201` |
| PUT | `/api/marcas/<id>` | JWT-Admin | Editar |
| DELETE | `/api/marcas/<id>` | JWT-Admin | Eliminar |

Request: `{"nombre": "Tocobo", "descripcion": "...", "logo_url": "https://..."}`.

### Carrito — `/api/carrito`

Por JWT con sesión, o header `X-Guest-Token` para invitados.

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| GET | `/api/carrito` | JWT o guest | Carrito con detalles |
| POST | `/api/carrito/items` | JWT o guest | `{"producto_id", "cantidad?"}` (valida stock) |
| PUT | `/api/carrito/items/<item_id>` | JWT o guest | Cambia cantidad (valida stock) |
| DELETE | `/api/carrito/items/<item_id>` | JWT o guest | Quita un ítem |
| DELETE | `/api/carrito` | JWT o guest | Vacía el carrito |

Códigos: `200/201` · `400` producto inactivo o stock insuficiente · `404`.

### Pedidos — `/api/pedidos`

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| POST | `/api/pedidos` | — (JWT opcional) | Checkout (autenticado: su carrito; invitado: carrito guest o `items`) |
| GET | `/api/pedidos` | JWT | Propios (`?page&per_page&estado`) o todos (admin) |
| GET | `/api/pedidos/<id>` | JWT o guest | Detalle (dueño, admin o invitado con `guest_token`/`email_contacto`) |
| PATCH | `/api/pedidos/<id>/estado` | JWT-Admin | Cambia estado + notifica (in-app y email) |
| PUT/POST | `/api/pedidos/<id>/guia` | JWT-Admin | Imagen de guía (`multipart`, `archivo`) |

Estados: `pendiente`, `confirmado`, `enviado`, `entregado`, `cancelado`. Al crear,
el stock se descuenta; si llega a 0 el producto pasa a `agotado`.

**POST `/api/pedidos`** autenticado: `{"direccion_envio": "12 Av. Zona 3, Xela"}`.
Invitado:

```json
{ "direccion_envio": "12 Av. Zona 3, Xela", 
  "email_contacto": "invitado@ejemplo.com",
  "telefono_contacto": "50255556666", 
  "items": [{ "producto_id": 2, "cantidad": 1 }] 
}
```

(`items` solo si el invitado no tiene carrito guest.) Response `201` con el pedido
(detalles con snapshot `precio_unitario`/`subtotal`/`nombre_producto`).
**PATCH `.../estado`**: `{"estado": "enviado"}` → `200` · `400` estado inválido.

### Favoritos — `/api/favoritos` (JWT)

`GET` lista · `POST /<producto_id>` agrega · `DELETE /<producto_id>` quita.

### Reseñas — `/api/resenas`

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| GET | `/api/resenas?producto=<id>` | — | Públicas por producto (+ `promedio`, `total`) |
| GET | `/api/resenas` | JWT-Admin | Todas |
| POST | `/api/resenas` | JWT | Solo si compró el producto, una por usuario+producto |
| PUT | `/api/resenas/<id>` | JWT-Admin | Editar |
| DELETE | `/api/resenas/<id>` | JWT-Admin | Eliminar |

**POST**: `{"producto_id": 2, "calificacion": 5, "comentario": "Me encantó"}` →
`201` · `400` duplicada/rango · `403` no compró · `404`.

### Notificaciones — `/api/notificaciones` (JWT)

`GET` últimas 50 + `no_leidas` · `PUT /<id>/leida` · `PUT /leer-todas` ·
`GET/POST/DELETE /producto/<id>/alerta` (alerta "avísame" de stock, única por
usuario+producto). Tipos: `pedido_estado`, `pedido_guia`, `producto_stock`.

### Reportes — `/api/reportes` (JWT-Admin)

Todos aceptan `desde=YYYY-MM-DD`, `hasta=YYYY-MM-DD` y `excel=1` (descarga
`.xlsx` vía openpyxl en lugar de JSON).

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/reportes/ventas-totales` | Total y nº de pedidos (excluye cancelados) |
| GET | `/api/reportes/ventas-por-mes` | Ventas por mes |
| GET | `/api/reportes/ventas-por-periodo` | Pedidos entre `desde` y `hasta` (obligatorios) |
| GET | `/api/reportes/ganancias` | Ventas vs. costos de movimientos `entrada` |
| GET | `/api/reportes/productos-mas-vendidos` | Top (`limit`, defecto 10) |
| GET | `/api/reportes/clientes-top` | Top (`limit`, defecto 10) |

`reportes.py` genera exclusivamente Excel; no incluye exportación a PDF.

## Migraciones

```bash
flask db upgrade                 # aplicar (en Docker: docker compose exec api flask db upgrade)
flask db current                 # ver migración actual
flask db migrate -m "cambio"     # crear tras modificar models/
flask db downgrade               # revertir la última
```

15 migraciones en `migrations/versions/`: inicial, recuperación de contraseña,
2FA, `guest_token` en carritos, email/teléfono y `usuario_id` nullable en
pedidos, `nombre_producto` + fusión de heads, snapshot `subtotal`,
galería de imágenes, `tamano`, `url_guia`, movimientos de inventario + costo,
notificaciones y alertas.

## Seeders

```bash
python seed.py   # en Docker: docker compose exec api python seed.py
```

Crea si no existe el admin: `admin@keibeauty.com` / `admin123` (rol `admin`),
3 marcas (COSRX, Beauty of Joseon, Some By Mi), 3 categorías (Limpieza,
Hidratación, Tratamiento) y 5 productos. El seed es mínimo (sin cliente de
prueba ni pedidos): para verificación rica se crea un cliente y pedidos desde
el frontend o la API.


## GitFlow

Ramas: 
- `main` (producción) · 
- `develop` (integración) · 
- `feature/*` (introduccion de funcionalidad)·
- `hotfix/*`. (arreglo rapido de un error).

## Despliegue

### Despliegue del frontend a través del backend (modo actual)

Por ahora el frontend se despliega servido por la API, en una sola URL:

- **Ruta:** `/` (y cualquier ruta SPA: `/catalogo`, `/sobre-nosotros`,
  `/config-api`) sirve `dist/index.html`; `/health` y `/api/*` siguen JSON.
- **Por qué así:** una sola URL para pruebas en teléfono con ngrok (un solo
  túnel), mismo origen (sin CORS entre tienda y API) y un solo servicio.
- **Cómo:** `npm run build` en el frontend + `STATIC_DIR=/frontend-dist` en el
  `.env` del backend (el `docker-compose.yml` ya monta
  `../KeiBeauty-frontend/dist:/frontend-dist:ro`) + `docker compose up -d api`.
  Sin `STATIC_DIR`, `/` devuelve el JSON informativo.

### Producción Docker

Imagen multi-etapa (`Dockerfile`, usuario `appuser`, Gunicorn 4 workers).
Componer con PostgreSQL gestionado, `FLASK_ENV=production`, secretos reales y
CORS restringido a los dominios finales, servido por HTTPS.

### Exponer con ngrok (probar desde el teléfono)

```bash
ngrok config add-authtoken <tu-authtoken>   # una sola vez
# En .env: CORS_ORIGINS_REGEX_EXTRA=https://.*\.ngrok-free\.app (una sola vez)
docker compose up -d api
ngrok http 5000   # una sola URL: tienda + API
```

Tienda: `https://<url>/` · Config API:
`https://<url>/config-api?api=https://<url>/api` (ver README del frontend).
`curl https://<url>/health` para verificar.

## Notas de seguridad

- Contraseñas con hash `pbkdf2` (Werkzeug); nunca en claro.
- Tokens de recuperación SHA-256, 24 h, un solo uso.
- 2FA: 6 dígitos hasheados, 5 min, 5 intentos, reenvío con rate limit 60 s.
- JWT: access 24 h + refresh 30 d + temporal 2FA 10 min (`estado=en_autenticacion`).
- CORS por entorno; en producción restringir orígenes y servir por HTTPS.
- Secretos solo en `.env` (no versionado).
- Stock validado y descontado en la transacción del pedido.
- Sin SQL crudo en ningún endpoint: todo pasa por SQLAlchemy con parámetros
  enlazados; la búsqueda por nombre escapa los comodines LIKE (`%`, `_`).

## Solución a posibles errores

| Problema | Solución |
|---|---|
| `relation already exists` en migrate | `flask db stamp head` si el esquema coincide, o recrear la BD |
| `connection refused` a PostgreSQL | En Docker el host es `db`; verificar `DATABASE_URL` y `db` healthy |
| CORS bloquea al frontend | Agregar el origen a `CORS_ORIGINS` (o regex ngrok) y recrear api |
| Emails 553 relay denegado (Zoho) | `FROM_EMAIL` igual a `SMTP_USER`; `SMTP_PASSWORD` de aplicación |
| Subida de imágenes 500 ImageKit | Faltan `IMAGEKIT_*`; usar `imagen_url` directa |
| Seed "ya existen" | `docker compose down -v` para reseedear (borra la BD) |
| Puerto 5000 ocupado | Cambiar mapeo o detener el proceso local |
| `permission denied` Docker (Linux) | `sudo usermod -aG docker $USER` y reiniciar sesión |

## Reconstruir imágenes Docker

Si modificaste dependencias (`requirements.txt`), el `Dockerfile` o el
`docker-compose.yml`, tenés que reconstruir las imágenes. La diferencia clave:
reconstruir **todo** borra la base de datos, reconstruir **solo el backend**
la conserva.

### Reconstruir todo desde cero

```bash
cd KeiBeauty

# Detener contenedores y borrar volúmenes (IMPORTANTE: borra la BD)
docker compose down -v

# Reconstruir imágenes sin caché
docker compose build --no-cache

# Levantar
docker compose up -d

# Aplicar migraciones
docker compose exec api flask db upgrade

# Correr seed
docker compose exec api python seed.py
```

> **Advertencia:** `docker compose down -v` elimina el volumen
> `postgres_data`, es decir, **borra por completo la base de datos**
> (`keibeauty_db`). Usalo solo si querés empezar desde cero (luego hay que
> aplicar migraciones y correr el seed).

### Reconstruir solo el backend (sin borrar la BD)

```bash
docker compose build --no-cache api
docker compose up -d api
```

Este flujo conserva el volumen de PostgreSQL, así que los datos quedan
intactos. Después verificá que la API aplicó las migraciones al arrancar
(el comando de arranque ya ejecuta `flask db upgrade`).

### Ver logs en vivo

```bash
docker compose logs -f api
docker compose logs -f db
```

### Limpiar imágenes huérfanas

```bash
docker image prune -a
docker volume prune
```

> `docker volume prune` borra **todos** los volúmenes no usados, incluida
> la BD si el contenedor está abajo. Revisá con `docker volume ls` antes.

### Cómo verificar que se reconstruyó bien

```bash
docker compose ps                          # api y db en estado Up/healthy
curl -i http://localhost:5000/health       # 200 {"status":"ok"}
docker compose exec api flask db current   # última migración aplicada
```
