import json
from pathlib import Path
from datetime import datetime

# ============================================================
# CLASES DE DATOS (definidas aquí, sin importar de 'modelos')
# ============================================================

class Usuario:
    def __init__(self, id_usuario, nombre, usuario, contraseña, rol):
        self.id_usuario = id_usuario
        self.nombre = nombre
        self.usuario = usuario
        self.contraseña = contraseña
        self.rol = rol

    def a_dict(self):
        return {
            "id_usuario": self.id_usuario,
            "nombre": self.nombre,
            "usuario": self.usuario,
            "contraseña": self.contraseña,
            "rol": self.rol
        }


class Producto:
    def __init__(self, codigo, nombre, categoria, precio, stock):
        self.codigo = codigo
        self.nombre = nombre
        self.categoria = categoria
        self.precio = precio
        self.stock = stock

    def a_dict(self):
        return {
            "codigo": self.codigo,
            "nombre": self.nombre,
            "categoria": self.categoria,
            "precio": self.precio,
            "stock": self.stock
        }


class Venta:
    def __init__(self, id_venta, usuario, producto, fecha=None):
        self.id_venta = id_venta
        self.usuario = usuario
        self.producto = producto
        self.fecha = fecha or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def a_dict(self):
        return {
            "id_venta": self.id_venta,
            "usuario": self.usuario,
            "producto": self.producto,
            "fecha": self.fecha
        }


# ============================================================
# SERVICIO DE ARCHIVOS
# ============================================================

class ArchivoServicio:
    def __init__(self, carpeta_datos):
        self.carpeta = Path(carpeta_datos)
        self.carpeta.mkdir(exist_ok=True)

    def leer_archivo(self, nombre_archivo):
        ruta = self.carpeta / nombre_archivo
        if not ruta.exists():
            return []
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)

    def escribir_archivo(self, nombre_archivo, datos):
        ruta = self.carpeta / nombre_archivo
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=4)


# ============================================================
# SERVICIO PRINCIPAL DEL RESTAURANTE
# ============================================================

class RestauranteServicio:
    def __init__(self, archivo_servicio):
        self.archivo = archivo_servicio
        self.usuarios = []
        self.productos = []
        self.ventas = []
        self._cargar_datos()

    def _cargar_datos(self):
        datos_usuarios = self.archivo.leer_archivo("usuarios.json")
        self.usuarios = [Usuario(**u) for u in datos_usuarios]

        datos_productos = self.archivo.leer_archivo("productos.json")
        self.productos = [Producto(**p) for p in datos_productos]

        datos_ventas = self.archivo.leer_archivo("ventas.json")
        self.ventas = [Venta(**v) for v in datos_ventas]

    def _guardar_todo(self):
        self.archivo.escribir_archivo("usuarios.json", [u.a_dict() for u in self.usuarios])
        self.archivo.escribir_archivo("productos.json", [p.a_dict() for p in self.productos])
        self.archivo.escribir_archivo("ventas.json", [v.a_dict() for v in self.ventas])

    # ------------------ LOGIN ------------------
    def validar_acceso(self, nombre_usuario, contraseña):
        for u in self.usuarios:
            if u.usuario == nombre_usuario and u.contraseña == contraseña:
                return u
        return None

    # ------------------ USUARIOS ------------------
    def listar_usuarios(self):
        return self.usuarios

    def cantidad_usuarios(self):
        return len(self.usuarios)

    def buscar_usuario_por_id(self, id_usuario):
        for u in self.usuarios:
            if str(u.id_usuario) == str(id_usuario):
                return u
        return None

    def registrar_usuario(self, id_usuario, nombre, usuario, contraseña, rol):
        if not all([id_usuario, nombre, usuario, contraseña, rol]):
            raise ValueError("Todos los campos son obligatorios")
        if any(str(u.id_usuario) == str(id_usuario) for u in self.usuarios):
            raise ValueError(f"El ID {id_usuario} ya existe")
        if any(u.usuario == usuario for u in self.usuarios):
            raise ValueError(f"El nombre de usuario '{usuario}' ya está en uso")
        self.usuarios.append(Usuario(id_usuario, nombre, usuario, contraseña, rol))
        self._guardar_todo()

    def actualizar_usuario(self, id_usuario, nombre, usuario, contraseña, rol, id_actual):
        u = self.buscar_usuario_por_id(id_usuario)
        if not u:
            raise ValueError("Usuario no encontrado")
        if not all([nombre, usuario, contraseña, rol]):
            raise ValueError("Todos los campos son obligatorios")
        u.nombre = nombre
        u.usuario = usuario
        u.contraseña = contraseña
        u.rol = rol
        self._guardar_todo()

    def eliminar_usuario(self, id_usuario, id_actual):
        if str(id_usuario) == str(id_actual):
            raise ValueError("No puede eliminar su propia cuenta")
        u = self.buscar_usuario_por_id(id_usuario)
        if not u:
            raise ValueError("Usuario no encontrado")
        self.usuarios.remove(u)
        self._guardar_todo()

    # ------------------ PRODUCTOS ------------------
    def listar_productos(self):
        return self.productos

    def cantidad_productos(self):
        return len(self.productos)

    def registrar_producto(self, codigo, nombre, categoria, precio, stock):
        if not all([codigo, nombre, categoria]) or precio <= 0 or stock < 0:
            raise ValueError("Datos incompletos o inválidos")
        if any(p.codigo == codigo for p in self.productos):
            raise ValueError(f"El código {codigo} ya existe")
        self.productos.append(Producto(codigo, nombre, categoria, precio, stock))
        self._guardar_todo()

    def actualizar_producto(self, codigo, nombre, categoria, precio, stock):
        p = next((x for x in self.productos if x.codigo == codigo), None)
        if not p:
            raise ValueError("Producto no encontrado")
        if not all([nombre, categoria]) or precio <= 0 or stock < 0:
            raise ValueError("Datos incompletos o inválidos")
        p.nombre = nombre
        p.categoria = categoria
        p.precio = precio
        p.stock = stock
        self._guardar_todo()

    def eliminar_producto(self, codigo):
        p = next((x for x in self.productos if x.codigo == codigo), None)
        if not p:
            raise ValueError("Producto no encontrado")
        self.productos.remove(p)
        self._guardar_todo()

    # ------------------ VENTAS ------------------
    def listar_ventas(self):
        return self.ventas

    def cantidad_ventas(self):
        return len(self.ventas)

    def registrar_venta(self, nombre_usuario, codigo_producto):
        usuario = next((u for u in self.usuarios if u.usuario == nombre_usuario), None)
        producto = next((p for p in self.productos if p.codigo == codigo_producto), None)

        if not usuario:
            raise ValueError("Usuario no encontrado")
        if not producto:
            raise ValueError("Producto no encontrado")
        if producto.stock <= 0:
            raise ValueError(f"Sin stock disponible para {producto.nombre}")

        nuevo_id = f"V{len(self.ventas)+1:03d}"
        producto.stock -= 1
        self.ventas.append(Venta(nuevo_id, usuario.usuario, producto.nombre))
        self._guardar_todo()