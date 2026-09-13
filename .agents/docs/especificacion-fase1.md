# Primera Fase Proyecto de Seminario de Sistemas 1: Kei Beauty

**Universidad de San Carlos de Guatemala**  
**Centro Universitario de Occidente (CUNOC)**  
**División de Ciencias de la Ingeniería**  
**Ingeniería en Ciencias y Sistemas**  
**Catedrático:** Ing. Mario Tobar  
**Fecha:** Quetzaltenango, 18 de agosto del 2026  

**Integrantes / Autores:**
* Sergio Alejandro Rodríguez López | 202131443
* Jorge Aníbal Bravo Rodríguez | 202131782

---

## 1. Descripción de la Empresa

* **Nombre de la empresa:** Kei Beauty (Kei Esencia)
* **Propietaria:** Karen Fernanda Calderón García
* **Contacto y Redes Sociales:**
  * Facebook: *Kei Esencia*
  * WhatsApp: *3971 8418*
* **Lema:** *"Tu ritual esencial - Skincare, K-Beauty, Cabello (Xela, Guatemala)"*

### Descripción General
Kei Beauty es una empresa dedicada a la comercialización de productos coreanos de belleza (K-Beauty), enfocándose principalmente en productos para el cuidado de la piel y del cabello. Opera desde el año 2021 y utiliza redes sociales (Facebook, Instagram y WhatsApp) como sus principales medios digitales de promoción, venta y atención al cliente.

---

## 2. Definición del Problema

El modelo de negocio actual de Kei Beauty presenta varias limitaciones operativas que afectan su crecimiento y eficiencia:

1. **Dependencia de canales manuales:** La gestión de pedidos, consultas de disponibilidad y atención al cliente se realizan exclusivamente por mensajes directos en redes sociales. Esto genera una carga de trabajo administrativa significativa para la propietaria, quien es la única responsable de todas las operaciones.
2. **Inventario desactualizado:** El control de inventario se realiza de forma manual y se actualiza aproximadamente una vez al mes. Esto provoca que los clientes consulten por productos que ya no están disponibles, generando frustración y pérdida de ventas.
3. **Falta de visibilidad y alcance:** La empresa depende de la exposición limitada de las redes sociales para llegar a nuevos clientes. No cuenta con un canal propio que le permita tener presencia constante y profesional en internet.
4. **Procesos ineficientes:** Desde la consulta hasta la entrega, todo el flujo de venta es manual y no centralizado. No hay un registro formal de clientes, historial de compras o análisis de ventas que permita tomar decisiones informadas.
5. **Escalabilidad limitada:** El modelo actual no es escalable. Si el negocio crece, la propietaria no podrá manejar la demanda con los procesos actuales.

---

## 3. Solución Propuesta

Desarrollar una plataforma web de comercio electrónico (tienda en línea) para centralizar y automatizar los procesos clave:

* **Centralizar el catálogo de productos:** Permitir la visualización de productos disponibles con información en tiempo real (nombre, imagen, precio, descripción y stock).
* **Automatizar el proceso de compra:** Permitir el registro de clientes, gestión de carrito de compras y generación de pedidos sin intervención manual previa.
* **Optimizar la gestión interna:** Proporcionar un panel de administración para gestionar productos, inventario, pedidos y clientes.
* **Mejorar la experiencia del cliente:** Habilitar la consulta de disponibilidad en tiempo real, seguimiento/guías de envío y promociones.
* **Generar reportes de negocio:** Proveer métricas clave (ventas por día/mes, productos más vendidos, ingresos, etc.) para facilitar la toma de decisiones.

---

## 4. Objetivos

### Objetivo General
Diseñar, desarrollar e implementar una plataforma web de comercio electrónico para la empresa Kei Esencia, que automatice y centralice sus procesos de venta, gestión de inventario y atención al cliente, mejorando su eficiencia operativa y su alcance en el mercado digital.

### Objetivos Específicos
* **Digitalizar el catálogo de productos:** Crear un módulo que permita a la administradora agregar, editar y eliminar productos, con información detallada y control de stock.
* **Automatizar el proceso de compra:** Implementar un carrito de compras y un flujo de pedidos intuitivo y amigable para el cliente.
* **Centralizar la gestión de pedidos:** Desarrollar un panel administrativo donde la propietaria pueda ver, actualizar el estado y gestionar todos los pedidos en un solo lugar.
* **Optimizar el control de inventario:** Implementar un sistema que actualice el stock automáticamente con cada compra y envíe alertas cuando los productos estén por agotarse.
* **Mejorar la experiencia del cliente:** Permitir el registro de usuarios, la gestión de perfiles, el historial de compras y lista de favoritos.
* **Proveer herramientas de análisis:** Generar reportes y gráficos que muestren el desempeño del negocio como ventas, productos populares, ingresos, etc.

---

## 5. Alcance del Proyecto

### Alcance Funcional
* **Módulo de Autenticación y Usuarios:**
  * Registro e inicio de sesión de clientes con sesiones seguras.
  * Gestión de perfiles de usuario.
  * Control de acceso basado en roles: *Administrador* (Propietaria) y *Cliente* (Usuario registrado / invitado).
* **Módulo de Productos:**
  * Catálogo público con filtros por categoría (*cuidado de la piel, cuidado del cabello*) y marca (*Centella, Tocobo, Lilipink*).
  * Vista detallada del producto (imagen, nombre, precio, descripción, stock).
  * Panel de gestión de productos para el administrador.
* **Módulo de Carrito y Pedidos:**
  * Carrito de compras (agregar, modificar cantidades, eliminar).
  * Proceso de checkout (confirmación de dirección y método de pago).
  * Historial de pedidos para clientes y panel de actualización de estados para la administradora.
* **Módulo de Notificaciones:**
  * Notificaciones por correo electrónico (confirmación de registro y pedidos).
* **Módulo de Reportes:**
  * Dashboard con métricas: ventas diarias/mensuales, productos más/menos vendidos, ingresos totales, estado de pedidos, stock bajo, ventas por marca/categoría.
* **Módulo de Comunicación:**
  * Integración de enlace directo/chat con WhatsApp para soporte al cliente.

### Alcance Técnico
* **Frontend:** SPA desarrollada con un framework moderno (React, Vue.js o Angular), alojada en **Amazon S3** y distribuida mediante **Amazon CloudFront**.
* **Backend:** API RESTful (Node.js, Python/Django/Flask o Java/Spring Boot), desplegada en instancias **Amazon EC2**.
* **Base de Datos:** Relacional **PostgreSQL**, gestionada con **Amazon RDS**.
* **Infraestructura Cloud:** Amazon Web Services (AWS).
* **CI/CD & DevOps:** GitHub Actions para integración/despliegue continuo.
* **Control de Versiones:** Git con flujo **GitFlow**.
* **Gestión de Proyecto:** Jira (metodología ágil por Sprints).

### Fuera de Alcance
* Desarrollo de aplicaciones móviles nativas (la web será adaptativa/responsive).
* Integración directa con sistemas de contabilidad o facturación electrónica.
* Integración API automatizada con empresas de logística/mensajería (las guías con la empresa Forza se gestionarán manualmente por ahora).
* Pasarela de pago con tarjeta en línea en la primera fase (se mantendrá el modelo de *pago contra entrega*).

---

## 6. Requisitos del Sistema

### Requisitos Funcionales (RF)

| ID | Requisito Funcional | Descripción | Prioridad |
|---|---|---|---|
| **RF-1** | Registro de Usuario | Permitir a los usuarios crear cuenta con nombre, correo, dirección y teléfono. | Alta |
| **RF-2** | Inicio de Sesión | Autenticación con correo y contraseña. | Alta |
| **RF-3** | Visualización de Catálogo | Mostrar productos con imagen, nombre, precio y disponibilidad. Filtros por categoría y marca. | Alta |
| **RF-4** | Detalle de Producto | Mostrar ficha completa del producto (descripción, stock, precio, etc.). | Alta |
| **RF-5** | Gestión de Carrito de Compras | Permitir agregar, modificar cantidad y eliminar productos del carrito. | Alta |
| **RF-6** | Proceso de Compra (Checkout) | Flujo para confirmar dirección de envío y finalizar el pedido. | Alta |
| **RF-7** | Historial de Pedidos del Cliente | Consultar pedidos anteriores realizados por el usuario. | Media |
| **RF-8** | Gestión de Productos (Admin) | Operaciones CRUD (Crear, Leer, Actualizar, Eliminar) de productos. | Alta |
| **RF-9** | Gestión de Pedidos (Admin) | Visualización y cambio de estados de pedidos (pendientes, enviados, etc.). | Alta |
| **RF-10** | Control de Inventario | Descuento automático de stock tras compras y ajuste manual por parte del admin. | Alta |
| **RF-11** | Alertas de Stock Bajo | Notificar al admin cuando el stock sea inferior a un umbral (ej. 5 unidades). | Media |
| **RF-12** | Panel de Reportes (Admin) | Dashboard con métricas comerciales clave e ingresos. | Alta |
| **RF-13** | Lista de Favoritos | Permitir a los clientes guardar productos en wishlist. | Baja |
| **RF-14** | Vinculación con WhatsApp | Enlace directo para comunicación fluida con la tienda. | Media |
| **RF-15** | Compra sin Registro | Permitir checkout como invitado proporcionando datos de contacto y envío. | Media |

### Requisitos No Funcionales (RNF)

| ID | Requisito No Funcional | Descripción | Prioridad |
|---|---|---|---|
| **RNF-1** | Disponibilidad | Alta disponibilidad del sistema en la nube. | Alta |
| **RNF-2** | Seguridad | Almacenamiento seguro de contraseñas (hashing), control de acceso por roles y protocolo HTTPS. | Alta |
| **RNF-3** | Usabilidad | Interfaz intuitiva, clara y fácil de usar. | Alta |
| **RNF-4** | Mantenibilidad | Código modular, bien documentado y siguiendo buenas prácticas. | Alta |
| **RNF-5** | Portabilidad | Compatibilidad con principales navegadores (Chrome, Firefox, Safari, Edge) y responsive design. | Alta |

---

## 7. Arquitectura e Infraestructura en la Nube (AWS)

La arquitectura está diseñada para ser económica, modular y escalable:

* **Amazon S3:** Hosting de archivos estáticos del frontend (HTML, CSS, JS, imágenes).
* **Amazon CloudFront:** CDN para distribución global de contenido estático con baja latencia y soporte de SSL/TLS.
* **Amazon EC2:** Servidor virtual donde se ejecuta la API REST del backend.
* **Amazon RDS:** Servicio administrado para la base de datos relacional PostgreSQL.
* **Amazon Route 53:** Gestión de DNS y dominios.
* **AWS Certificate Manager (ACM):** Gestión de certificados SSL/TLS para HTTPS.
* **AWS IAM:** Gestión de políticas de acceso e identidades bajo el principio de mínimo privilegio.
* **AWS Secrets Manager:** Almacenamiento seguro de credenciales y claves secretas de la aplicación.
* **Amazon CloudWatch:** Monitoreo y logs de infraestructura.

### Flujo de Arquitectura
1. **Contenido Estático:** `Usuario -> Route 53 -> CloudFront -> Amazon S3 (Frontend)`
2. **Lógica de Negocio:** `Usuario -> Route 53 -> CloudFront -> Amazon EC2 (Backend REST API) -> Amazon RDS (PostgreSQL)`

---

## 8. Análisis Económico

### Costos Estimados de Desarrollo
* **Recurso Humano:** 2 desarrolladores × 3 meses = **Q 30,000.00** (Q 5,000.00 / mes cada uno)
* **Infraestructura de Desarrollo (AWS):** Q 150.00 - Q 300.00
* **Herramientas (Jira, GitHub):** Q 0.00 (Planes gratuitos)
* **Total Estimado de Desarrollo:** **Q 30,150.00 – Q 30,300.00**

### Costos Estimados de Operación Mensual (Nube AWS)

| Servicio AWS / Recurso | Uso Estimado | Costo Mensual (USD) | Costo Mensual Estimado (GTQ) |
|---|---|---|---|
| **Amazon S3** | Alojamiento frontend e imágenes | $0.50 - $2.00 | Q 3.85 - Q 15.40 |
| **Amazon EC2** | Backend API (Instancia pequeña) | $8.00 - $12.00 | Q 61.60 - Q 92.40 |
| **Amazon RDS** | DB PostgreSQL administrada | $15.00 - $25.00 | Q 115.50 - Q 192.50 |
| **Amazon CloudFront** | CDN y distribución | $0.00 - $5.00 | Q 0.00 - Q 38.50 |
| **Amazon Route 53** | Gestión de DNS | ~$0.50 - $1.00 | Q 3.85 - Q 7.70 |
| **AWS Certificate Manager** | Certificado SSL/TLS | $0.00 | Q 0.00 |
| **Dominio (.com)** | Prorrateado anual | ~$1.00 - $2.00 | Q 7.70 - Q 15.40 |
| **TOTAL ESTIMADO** | Operación Mensual | **~$25 - $47** | **~Q 193.00 - Q 362.00** |

---

## 9. Análisis de Riesgos

| Riesgo | Probabilidad | Impacto | Estrategia de Mitigación |
|---|---|---|---|
| **Retrasos en el desarrollo** | Media | Alto | Sprints de 3 semanas con entregables claros y reuniones semanales. |
| **Cambios en requisitos** | Media | Medio | Comunicación constante con la clienta, gestión formal de cambios vía Backlog en Jira. |
| **Falta de conocimiento técnico** | Baja | Alto | Capacitación e investigación previa sobre AWS, frameworks y buenas prácticas. |
| **Fallo en la infraestructura cloud** | Baja | Alto | Uso de servicios gestionados por AWS (RDS, S3) con alta disponibilidad implícita. |
| **Baja adopción por clientes** | Media | Medio | Campaña en redes sociales, promociones de lanzamiento para primeros compradores. |
| **Problemas de seguridad** | Baja | Alto | Aplicación de *Security by Design*, cifrado de datos/contraseñas y gestión estricta de roles. |

---

## 10. Flujos de Trabajo y Procesos (BPMN)

### 1. Proceso Actual de Pedido (Manual)
1. La propietaria publica un producto en redes sociales.
2. El cliente consulta disponibilidad y precio por mensaje directo.
3. La propietaria verifica el inventario manualmente y responde.
4. El cliente confirma la compra y provee datos de entrega.
5. La propietaria anota el pedido, empaqueta el producto, genera la guía de mensajería y actualiza el inventario en sus registros manuales.

### 2. Proceso Propuesto de Compra (Automatizado)
1. El cliente accede a la web y navega en el catálogo.
2. Agrega productos al carrito.
3. Procede al checkout, ingresa datos de envío y confirma el pedido.
4. El sistema registra el pedido en estado *Pendiente*, descuenta automáticamente el stock y envía correo de confirmación.

### 3. Proceso de Gestión de Inventario y Pedidos (Administrador)
1. La administradora ingresa al dashboard.
2. Visualiza alertas de stock bajo y pedidos entrantes.
3. Procesa los pedidos actualizando el estado y adjuntando número de guía de envío.

---

## 11. Casos de Uso Clave

* **CU-1: Registrar Usuario:** Formulario de captura de datos con validaciones (correo único).
* **CU-2: Iniciar Sesión:** Validación de credenciales y asignación de JWT/Sesión.
* **CU-3 / CU-4: Catálogo y Detalle:** Búsqueda, filtros por marca/categoría y visualización de stock.
* **CU-5 / CU-6: Carrito y Checkout:** Selección de cantidades, resumen de montos y confirmación de compra (soporta compra como invitado).
* **CU-8: Gestión de Productos (Admin):** Panel CRUD completo para mantenimiento de catálogo.
* **CU-11: Panel de Reportes (Admin):** Visualización interactiva de KPIs de venta.

---

## 12. Metodología de Desarrollo y Herramientas

* **Estrategia de Ramificación (GitFlow):**
  * `main`: Producción (código estable).
  * `develop`: Integración de funcionalidades.
  * `feature/*`: Desarrollo de nuevas características.
  * `hotfix/*`: Correcciones de emergencia en producción.
* **Gestión del Proyecto:** Jira Software (Sprints, backlog de tareas e historias de usuario).

---

## 13. Diseño de Interfaz (Wireframes / Mockups)

El documento preliminar incluye prototipos de pantalla para:
1. **Catálogo Principal:** Barra de navegación, filtros laterales por rango de precio (Q0 - Q200) y marcas (Centella, Tocobo, Lilipink), grilla de productos con opción de agregar al carrito y etiquetas de oferta.
2. **Vista Detalle de Producto:** Galería de imágenes, descripción del producto, indicador de stock, botón de favoritos, selector de cantidad y precio.
3. **Carrito de Compras:** Detalle de ítems seleccionados, desglose de Subtotal, Costo de Envío (Q30.00) y Total, con botón directo a finalizar pago (esto es solo de ejemplo).
4. **Módulo de Autenticación:** Formulario limpio de inicio de sesión con validación de credenciales.
