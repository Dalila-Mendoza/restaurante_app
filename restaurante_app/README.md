# Sistema de Gestión para Restaurante
Es un sistema de administración de restaurante desarrollado en Python utilizando Programación Orientada a Objetos e interfaz gráfica con Tkinter. El proyecto permite gestionar productos, usuarios y registrar ventas, mediante una arquitectura modular que separa modelos, servicios y vistas.

# Datos del estudiante
**Dalila Yamilet Mendoza Bravo**

# Estructura del proyecto
restaurante_app/
├── modelos/
│ ├── init.py
│ ├── producto.py
│ ├── usuario.py
│ └── venta.py
├── datos/
│ ├── productos.json
│ ├── usuarios.json
│ └── ventas.json
├── servicios/
│ ├── init.py
│ ├── restaurante_servicio.py
│ └── archivo_servicio.py
├── ui/
│ ├── init.py
│ ├── login_view.py
│ └── main_view.py
├── assets/
├── main.py
└── README.md

# Responsabilidad de cada clase

# Producto
Representa los productos disponibles en el restaurante.
**Atributos:** Código, Nombre, Categoría, Precio, Stock.

# Usuario
Representa a las personas registradas en el sistema.
**Atributos:** Identificación, Nombre, Correo, Usuario, Contraseña.

# Venta
Representa una transacción realizada.
**Atributos:** ID de venta, Usuario, Producto, Fecha y hora.
**Métodos:** `a_diccionario()`, `desde_diccionario()` — para guardar y cargar desde JSON.

# RestauranteServicio
Administra las colecciones de productos, usuarios y ventas.
**Operaciones principales:**
- ✅ Registrar producto
- 🔍 Buscar producto
- ✏️ Actualizar producto
- 🗑️ Eliminar producto
- 📋 Listar productos
- 👤 Registrar y listar usuarios
- 💰 Registrar venta
- 📊 Listar ventas
- 🔽 Obtener listas para selección (usuarios y productos)

# ArchivoServicio
Gestiona la persistencia de datos.
- Carga información desde archivos JSON al iniciar
- Guarda automáticamente tras cada modificación
- Manejo de excepciones: `FileNotFoundError`, `JSONDecodeError`, `PermissionError`, `KeyError`, `ValueError`

# Estructuras de datos utilizadas
- **Lista** → Almacena objetos Producto, Usuario y Venta
- **Tupla** → Opciones del menú (no cambian en ejecución)
- **Diccionario** → Conversión de objetos para guardar en JSON
- **Conjunto** → Obtener categorías sin repetición

# Características implementadas y mejoras realizadas

# Acceso al sistema
- ✅ Inicio de sesión validado
- ✅ Cierre de sesión y regreso a pantalla de inicio

# Gestión completa de productos
- ✅ Registrar, consultar, actualizar y eliminar productos
- ✅ Validación de códigos duplicados y datos numéricos
- ✅ Visualización en tabla con formato

# Gestión de usuarios
- ✅ Visualización en tabla
- ✅ Carga desde `usuarios.json`

# Gestión de ventas — Novedad Semana 15
- ✅ Modelo `Venta` con `@property` (solo lectura)
- ✅ Formulario con listas desplegables: seleccionar usuario y producto
- ✅ Botón con `command=` y función callback para registrar
- ✅ Validación: verificar que existan ambos antes de registrar
- ✅ ID de venta automático
- ✅ Fecha y hora automática al registrar
- ✅ Tabla con todas las ventas realizadas
- ✅ Guardado en `ventas.json`
- ✅ Los datos se conservan al cerrar y reabrir la aplicación

# Interfaz gráfica mejorada
- ✅ Pantalla de inicio de sesión
- ✅ Panel principal con secciones: Productos / Usuarios / Ventas
- ✅ Tablas con encabezados claros
- ✅ Mensajes de confirmación y error

# Arquitectura y persistencia
- ✅ Separación de responsabilidades: modelos → servicios → vistas
- ✅ Carga automática al iniciar
- ✅ Persistencia real: los datos no se pierden al cerrar

# Validaciones implementadas
- ✅ Campos obligatorios no vacíos
- ✅ Valores numéricos correctos
- ✅ Existencia de usuario y producto antes de registrar venta
- ✅ Manejo seguro de archivos JSON

# Credenciales de acceso
| Usuario | Contraseña |
|---|---|
| `administradora` | `0804243798` |
| `empleado` | `1234567890` |

# Ejecución
```bash
python main.py

