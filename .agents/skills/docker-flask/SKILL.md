---
name: docker-flask
description: Se activa al crear, modificar o depurar archivos Dockerfile, docker-compose.yml, variables de entorno (.env) o requerimientos de dependencias (requirements.txt) en el backend.
tools:
  - codebase_search
  - file_editor
---

# Contenedorización del Backend con Docker

## Contexto de Aplicación
Usa esta habilidad cuando se requiera cambiar configuraciones de red, puertos exponenciales, dependencias del sistema operativo en el contenedor o variables de entorno para conectar Flask con PostgreSQL.

## Reglas Estrictas de Configuración

1. **Gestión de Dependencias:**
   - Cada vez que agregues librerías de Python en el código, debes actualizar inmediatamente el archivo `requirements.txt`.
   - Asegurar el uso de builds multi-etapa (*multi-stage builds*) en el `Dockerfile` para mantener la imagen ligera y segura.

2. **Seguridad y Ejecución:**
   - **Prohibido:** No correr la aplicación como usuario `root` dentro del contenedor. Configurar un usuario sin privilegios.
   - Utilizar un servidor WSGI como **Gunicorn** para producción en lugar del servidor de desarrollo de Flask.

3. **Variables de Entorno:**
   - No expongas contraseñas o credenciales de PostgreSQL en el `Dockerfile` o `docker-compose.yml`. 
   - Utilizar un archivo `.env.example` referencial y jalar las variables mediante `os.environ.get()`.
