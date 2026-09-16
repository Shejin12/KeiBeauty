---
name: convenciones-flask
description: Se activa al crear, modificar o auditar endpoints, rutas, controladores o interacciones con PostgreSQL dentro del backend de la tienda KeiBeauty.
tools:
  - codebase_search
  - file_editor
---

# Desarrollo de API con Flask - KeiBeauty

## Contexto de Aplicación
Utiliza esta habilidad siempre que se te pida diseñar, refactorizar o solucionar problemas en las capas de enrutamiento, controladores y persistencia de datos del backend del e-commerce.

## Flujo de Trabajo y Reglas Estrictas

1. **Modularidad (Blueprints):** 
   - Ubicar los manejadores de rutas exclusivamente dentro de sus respectivos Blueprints en el directorio `routes/` o `controllers/`.
   - No registrar rutas directamente en la instancia global de la aplicación (`app`).

2. **Validación de Entradas:** 
   - Sanitizar y validar los datos de entrada (JSON, query params, form data) *antes* de realizar consultas a la base de datos.
   - Retornar un error de validación inmediato si faltan campos obligatorios (especialmente crítico en el flujo de carrito y checkout).

3. **Persistencia (SQLAlchemy):** 
   - Utilizar modelos de SQLAlchemy definidos en `models/` para todas las interacciones con la base de datos PostgreSQL.
   - Evitar por completo el uso de consultas SQL en texto plano (raw SQL) para prevenir inyecciones.

4. **Control de Excepciones y Respuestas:** 
   - Manejar errores potenciales con bloques `try/except` específicos.
   - Devolver respuestas en formato JSON con mensajes de error claros y el código de estado HTTP correspondiente:
     - `400` para peticiones incorrectas o fallas de validación de stock o datos.
     - `401` / `403` para problemas de autenticación o autorización de clientes/admins.
     - `404` para recursos no encontrados (productos agotados, categorías inexistentes, etc.).
     - `500` para errores internos del servidor.
