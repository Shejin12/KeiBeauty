# CONFIGURACIÓN DEL AGENTE - KEIBEAUTY BACKEND

## Contexto de Negocio
- **Proyecto:** Kei Beauty (E-commerce de productos coreanos de belleza / K-Beauty).
- **Propósito:** API REST para gestionar el catálogo de productos de cuidado facial y maquillaje, autenticación de clientes y administradores, inventario, carrito de compras y procesamiento de pedidos.
- **Entidades Clave:** Usuarios (Clientes/Admins), Productos (Sérums, Limpiadores, Tónicos, etc.), Categorías, Marcas, Pedidos, Detalle de Pedidos y Reseñas.

## Stack Tecnológico
- **Lenguaje/Framework:** Python 3.11+, Flask (Patrón Blueprint).
- **Base de Datos:** PostgreSQL con SQLAlchemy ORM.
- **Estrategia de Ramas:** GitFlow (`main`, `develop`, `feature/*`).

## Habilidades Vinculadas
- `convenciones-flask`: Reglas obligatorias para la creación de rutas, controladores y queries en la API.
- `docker-flask`: Directrices de contenedorización, dependencias con Gunicorn, PostgreSQL y variables de entorno.

## Reglas para el Asistente
1. Responder siempre en español.
2. Aplicar validaciones estrictas en pedidos e inventario (ej. verificar stock antes de confirmar una compra).
3. Mantener endpoints limpios en `routes/` usando Blueprints y modelos en `models/`.
