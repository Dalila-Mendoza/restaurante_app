import inspect
import json
import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

TITULO_APP = "RESTAURANTE"
COLOR_MENU = "#16213b"
COLOR_BOTON = "#233459"
COLOR_ACTIVO = "#254bdb"
# Carpeta donde se guardan productos y ventas: restaurante_app/datos
RUTA_DATOS = Path(__file__).resolve().parent.parent / "datos"


USUARIOS_INICIALES = [
    {"id_usuario": "U001", "nombre": "Administrador", "usuario": "admin", "contraseña": "1234", "rol": "Propietario"},
    {"id_usuario": "U002", "nombre": "Trabajador", "usuario": "Trab", "contraseña": "abcd", "rol": "Empleado"},
    {"id_usuario": "U003", "nombre": "Ana Ezpinoza", "usuario": "ana", "contraseña": "cliente1", "rol": "Cliente"},
]
CAMPOS_USUARIO = {"id_usuario", "nombre", "usuario", "contraseña", "rol"}

PRODUCTOS_INICIALES = [
    {"codigo": "P001", "nombre": "Filete de corvina", "categoria": "Comida", "precio": 5.0, "stock": 12},
    {"codigo": "C222", "nombre": "Hamburguesa", "categoria": "Comida rapida", "precio": 4.5, "stock": 10},
    {"codigo": "P234", "nombre": "Coca-Cola", "categoria": "Bebida", "precio": 1.0, "stock": 10},
    {"codigo": "AK04", "nombre": "Batido de manjar", "categoria": "Dulces", "precio": 1.5, "stock": 15},
    {"codigo": "CP10", "nombre": "Hornado al barril", "categoria": "Comida", "precio": 15.0, "stock": 15},
    {"codigo": "Q123", "nombre": "Chaulafan", "categoria": "Comida rapida", "precio": 8.0, "stock": 15},
]
CAMPOS_PRODUCTO = {"codigo", "nombre", "categoria", "precio", "stock"}

# ======================= COMPATIBILIDAD CON LA CLASE Venta DEL SERVICIO =======================
def clase_venta(servicio):
    """Busca la clase Venta que usa tu RestauranteServicio."""
    if servicio is None:
        return None
    modulo = sys.modules.get(type(servicio).__module__)
    clase = getattr(modulo, "Venta", None)
    if clase is None and getattr(servicio, "ventas", None):
        clase = type(servicio.ventas[0])
    return clase


def valor_para(nombre, v):
    """Elige qué dato de la venta corresponde a un campo de la clase Venta (por su nombre)."""
    if "fecha" in nombre:
        return v["fecha"]
    if "cantidad" in nombre:
        return v["cantidad"]
    if "precio" in nombre:
        return round(v["total"] / v["cantidad"], 2) if v["cantidad"] else 0.0
    if any(k in nombre for k in ("total", "monto", "importe")):
        return v["total"]
    if any(k in nombre for k in ("vendedor", "empleado", "usuario", "mesero", "cajero")):
        if "id" in nombre or "codigo" in nombre:
            return v.get("vendedor_id", "")
        return v.get("vendedor", "")
    if any(k in nombre for k in ("producto", "plato", "articulo", "item")):
        if "id" in nombre or "codigo" in nombre:
            return v["producto_id"]
        return v["producto"]
    if nombre == "id" or nombre.startswith("id_") or nombre.endswith("_id") \
            or "codigo" in nombre or "numero" in nombre:
        return v["id"]
    return None


def armar_campos_venta(clase, v):
    """Devuelve un dict con los campos de Venta, o un texto explicando qué falta."""
    parametros = inspect.signature(clase.__init__).parameters
    datos, faltan = {}, []
    for nombre, par in parametros.items():
        if nombre == "self" or par.kind in (par.VAR_POSITIONAL, par.VAR_KEYWORD):
            continue
        valor = valor_para(nombre.lower(), v)
        if valor is None:
            if par.default is par.empty:
                faltan.append(nombre)
            continue
        datos[nombre] = valor
    if faltan:
        return "No sé qué dato poner en estos campos de Venta: " + ", ".join(faltan)
    return datos


# ======================= DATOS EN MEMORIA =======================
class Datos:
    """Datos de ejemplo compartidos por todas las pantallas.
    Se pierden al cerrar la app (más adelante se pueden guardar en archivo)."""

    def __init__(self, servicio=None):
        self.servicio = servicio
        self.aviso_ventas = False
        self.usuarios = self.cargar_usuarios()
        self.productos = self.cargar_productos()
        self.ventas = self.cargar_ventas()

    def cargar_usuarios(self):
        """Lee usuarios.json; si no existe o tiene otro formato, usa tus usuarios iniciales."""
        lista = self.cargar("usuarios.json", None)
        valido = isinstance(lista, list) and all(
            isinstance(u, dict) and CAMPOS_USUARIO <= set(u) for u in lista)
        if not valido:
            return [dict(u) for u in USUARIOS_INICIALES]
        return lista

    def cargar_ventas(self):
        """Lee registro_ventas.json y completa los campos que falten para que nunca rompa la pantalla."""
        lista = self.cargar("registro_ventas.json", [])
        if not isinstance(lista, list):
            return []
        ventas, usados = [], set()
        for n, v in enumerate(lista, start=1):
            if not isinstance(v, dict):
                continue
            ident, k = str(v.get("id", "")), n
            while not ident or ident in usados:
                ident, k = f"V{k:03d}", k + 1
            usados.add(ident)
            try:
                cantidad, total = int(v.get("cantidad", 0)), float(v.get("total", 0))
            except (TypeError, ValueError):
                cantidad, total = 0, 0.0
            venta = dict(v)
            venta.update({
                "id": ident, "fecha": str(v.get("fecha", "")),
                "producto_id": str(v.get("producto_id", v.get("codigo", ""))),
                "producto": str(v.get("producto", v.get("nombre", ""))),
                "cantidad": cantidad, "total": total})
            ventas.append(venta)
        return ventas

    def cargar_productos(self):
        """Lee productos.json; si no existe o tiene otro formato, usa tus productos iniciales."""
        lista = self.cargar("productos.json", None)
        valido = isinstance(lista, list) and all(
            isinstance(p, dict) and CAMPOS_PRODUCTO <= set(p) for p in lista)
        if not valido:
            return [dict(p) for p in PRODUCTOS_INICIALES]
        return lista

    @staticmethod
    def cargar(nombre, por_defecto):
        """Lee un archivo JSON de la carpeta datos; si no existe usa los valores por defecto."""
        try:
            with open(RUTA_DATOS / nombre, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, ValueError):
            return por_defecto

    def guardar(self):
        """Guarda usuarios, productos y ventas (también en ventas.json si el formato de Venta lo permite)."""
        try:
            RUTA_DATOS.mkdir(exist_ok=True)
            for nombre, contenido in (("usuarios.json", self.usuarios),
                                      ("productos.json", self.productos),
                                      ("registro_ventas.json", self.ventas)):
                with open(RUTA_DATOS / nombre, "w", encoding="utf-8") as f:
                    json.dump(contenido, f, ensure_ascii=False, indent=2)
        except OSError as error:
            messagebox.showerror("Error al guardar", str(error))
        error = self.guardar_ventas_servicio()
        if error and not self.aviso_ventas:  # el aviso sale una sola vez por sesión
            self.aviso_ventas = True
            messagebox.showwarning(
                "Ventas",
                "No se pudo escribir ventas.json:\n" + error +
                "\n\nLas ventas sí se guardan en registro_ventas.json.")

    def guardar_ventas_servicio(self):
        """Escribe ventas.json con los campos que acepta la clase Venta de tu servicio.
        Devuelve None si salió bien, o un texto con el problema (nunca rompe la app)."""
        try:
            clase = clase_venta(self.servicio)
            if clase is None:
                return "No se encontró la clase Venta en tu servicio."
            registros = []
            for v in self.ventas:
                datos = armar_campos_venta(clase, v)
                if isinstance(datos, str):
                    return datos
                clase(**datos)  # prueba: si Venta lo rechaza, no se escribe nada
                registros.append(datos)
            RUTA_DATOS.mkdir(exist_ok=True)
            with open(RUTA_DATOS / "ventas.json", "w", encoding="utf-8") as f:
                json.dump(registros, f, ensure_ascii=False, indent=2)
            return None
        except Exception as error:
            return f"{type(error).__name__}: {error}"


# ======================= UTILIDADES =======================
def siguiente_id(prefijo, items, clave="id"):
    numeros = [int(i[clave][len(prefijo):]) for i in items
               if i[clave].startswith(prefijo) and i[clave][len(prefijo):].isdigit()]
    return f"{prefijo}{max(numeros, default=0) + 1:03d}"


def buscar(items, identificador, clave="id"):
    for item in items:
        if item[clave] == identificador:
            return item
    return None


def dinero(valor):
    return f"${valor:,.2f}"


def crear_tabla(parent, columnas):
    """columnas: lista de (clave, titulo, ancho, alineacion)."""
    cont = tk.Frame(parent)
    cont.pack(fill=tk.BOTH, expand=True)
    tabla = ttk.Treeview(cont, columns=[c[0] for c in columnas], show="headings", height=15)
    for clave, titulo, ancho, alineacion in columnas:
        tabla.heading(clave, text=titulo)
        tabla.column(clave, width=ancho, anchor=alineacion)
    barra = ttk.Scrollbar(cont, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=barra.set)
    tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    barra.pack(side=tk.RIGHT, fill=tk.Y)
    return tabla


def crear_titulo(parent, texto):
    tk.Label(parent, text=texto, font=("Arial", 20, "bold"),
             bg="white").pack(anchor="w", pady=(0, 20))


def crear_botones(parent, botones, fila_inicial):
    """botones: lista de (texto, color, comando). Todo con grid."""
    for i, (texto, color, comando) in enumerate(botones):
        tk.Button(parent, text=texto, bg=color, fg="white",
                  font=("Arial", 12, "bold"), pady=8, command=comando
                  ).grid(row=fila_inicial + i, column=0, columnspan=2, sticky="ew", pady=4)


def limpiar_seleccion(tabla):
    tabla.selection_set(())


# ======================= INICIO =======================
class InicioView(tk.Frame):
    def __init__(self, parent, datos):
        super().__init__(parent, bg="white")
        self.datos = datos
        crear_titulo(self, "Inicio")

        fila = tk.Frame(self, bg="white")
        fila.pack(fill=tk.X)
        self.valores = {}
        colores = ["#2563eb", "#16a34a", "#d97706", "#7c3aed"]
        for i, (clave, titulo) in enumerate([
                ("usuarios", "Usuarios"), ("productos", "Productos"),
                ("ventas", "Ventas de hoy"), ("ingresos", "Ingresos de hoy")]):
            tarjeta = tk.Frame(fila, bg=colores[i], padx=20, pady=15)
            tarjeta.grid(row=0, column=i, padx=(0, 12), sticky="nsew")
            fila.columnconfigure(i, weight=1)
            tk.Label(tarjeta, text=titulo, bg=colores[i], fg="white",
                     font=("Arial", 11)).pack(anchor="w")
            lbl = tk.Label(tarjeta, text="0", bg=colores[i], fg="white",
                           font=("Arial", 22, "bold"))
            lbl.pack(anchor="w")
            self.valores[clave] = lbl

        tk.Label(self, text="Productos con stock bajo (5 o menos)", bg="white",
                 font=("Arial", 13, "bold")).pack(anchor="w", pady=(25, 8))
        self.lista_bajo = tk.Listbox(self, height=8, font=("Arial", 11))
        self.lista_bajo.pack(fill=tk.X)

    def refresh(self):
        d = self.datos
        hoy = datetime.now().strftime("%Y-%m-%d")
        ventas_hoy = [v for v in d.ventas if v["fecha"].startswith(hoy)]
        self.valores["usuarios"].config(text=str(len(d.usuarios)))
        self.valores["productos"].config(text=str(len(d.productos)))
        self.valores["ventas"].config(text=str(len(ventas_hoy)))
        self.valores["ingresos"].config(text=dinero(sum(v["total"] for v in ventas_hoy)))
        self.lista_bajo.delete(0, tk.END)
        bajos = [p for p in d.productos if p["stock"] <= 5]
        if not bajos:
            self.lista_bajo.insert(tk.END, "Todo el inventario está en orden.")
        for p in bajos:
            self.lista_bajo.insert(tk.END, f"{p['nombre']}  -  quedan {p['stock']}")


# ======================= USUARIOS =======================
class UsuariosView(tk.Frame):
    ROLES = ["Propietario", "Empleado", "Cliente"]

    def __init__(self, parent, datos):
        super().__init__(parent, bg="white")
        self.datos = datos
        crear_titulo(self, "Gestión de usuarios")

        form = tk.LabelFrame(self, text="Datos del usuario", padx=10, pady=10)
        form.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        self.entries = {}
        for i, texto in enumerate(["Identificador", "Nombre", "Usuario", "Contraseña"]):
            tk.Label(form, text=texto).grid(row=i, column=0, sticky="w", pady=8)
            entry = tk.Entry(form, width=26, show="*" if texto == "Contraseña" else "")
            entry.grid(row=i, column=1, pady=8, padx=10)
            self.entries[texto] = entry

        tk.Label(form, text="Rol").grid(row=4, column=0, sticky="w", pady=8)
        self.combo_rol = ttk.Combobox(form, values=self.ROLES, state="readonly", width=23)
        self.combo_rol.set(self.ROLES[-1])
        self.combo_rol.grid(row=4, column=1, pady=8, padx=10)

        crear_botones(form, [
            ("+  Registrar", "#2563eb", self.registrar),
            ("✏  Actualizar", "#3b82f6", self.actualizar),
            ("🗑  Eliminar", "#dc2626", self.eliminar),
            ("🧹  Limpiar", "#1e293b", self.limpiar),
        ], 5)

        marco = tk.LabelFrame(self, text="Usuarios registrados", padx=10, pady=10)
        marco.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.tabla = crear_tabla(marco, [
            ("id", "Identificador", 90, "center"), ("nombre", "Nombre", 150, "w"),
            ("usuario", "Usuario", 100, "w"), ("rol", "Rol", 100, "center")])
        self.tabla.bind("<<TreeviewSelect>>", self.seleccionar)

    def refresh(self):
        self.datos.guardar()
        self.tabla.delete(*self.tabla.get_children())
        for u in self.datos.usuarios:
            self.tabla.insert("", tk.END, iid=u["id_usuario"],
                              values=(u["id_usuario"], u["nombre"], u["usuario"], u["rol"]))

    def poner_id(self, texto, editable):
        e = self.entries["Identificador"]
        e.config(state="normal")
        e.delete(0, tk.END)
        e.insert(0, texto)
        if not editable:  # el identificador de un usuario existente no se cambia
            e.config(state="disabled")

    def registrar(self):
        ident = self.entries["Identificador"].get().strip()
        nombre = self.entries["Nombre"].get().strip()
        usuario = self.entries["Usuario"].get().strip()
        clave = self.entries["Contraseña"].get()
        if not (nombre and usuario and clave):
            messagebox.showwarning("Datos incompletos", "Completa nombre, usuario y contraseña.")
            return
        if not ident:  # si lo dejas vacío, se asigna el siguiente (U004, U005...)
            ident = siguiente_id("U", self.datos.usuarios, "id_usuario")
        if any(u["id_usuario"].lower() == ident.lower() for u in self.datos.usuarios):
            messagebox.showerror("Error", f"Ya existe un usuario con el identificador {ident}.")
            return
        if any(u["usuario"].lower() == usuario.lower() for u in self.datos.usuarios):
            messagebox.showerror("Error", f"El usuario '{usuario}' ya existe.")
            return
        self.datos.usuarios.append({
            "id_usuario": ident, "nombre": nombre, "usuario": usuario,
            "contraseña": clave, "rol": self.combo_rol.get()})
        self.limpiar()
        self.refresh()

    def actualizar(self):
        sel = self.tabla.selection()
        if not sel:
            messagebox.showwarning("Actualizar", "Selecciona un usuario de la tabla.")
            return
        u = buscar(self.datos.usuarios, sel[0], "id_usuario")
        nombre = self.entries["Nombre"].get().strip()
        usuario = self.entries["Usuario"].get().strip()
        if not (nombre and usuario):
            messagebox.showwarning("Datos incompletos", "Nombre y usuario son obligatorios.")
            return
        if any(o["usuario"].lower() == usuario.lower() and o["id_usuario"] != u["id_usuario"]
               for o in self.datos.usuarios):
            messagebox.showerror("Error", f"El usuario '{usuario}' ya existe.")
            return
        u["nombre"], u["usuario"], u["rol"] = nombre, usuario, self.combo_rol.get()
        clave = self.entries["Contraseña"].get()
        if clave:  # vacía = conservar la contraseña anterior
            u["contraseña"] = clave
        self.limpiar()
        self.refresh()

    def eliminar(self):
        sel = self.tabla.selection()
        if not sel:
            messagebox.showwarning("Eliminar", "Selecciona un usuario de la tabla.")
            return
        u = buscar(self.datos.usuarios, sel[0], "id_usuario")
        if messagebox.askyesno("Eliminar", f"¿Eliminar al usuario {u['nombre']}?"):
            self.datos.usuarios.remove(u)
            self.limpiar()
            self.refresh()

    def limpiar(self):
        for clave in ("Nombre", "Usuario", "Contraseña"):
            self.entries[clave].delete(0, tk.END)
        self.poner_id("", True)
        self.combo_rol.set(self.ROLES[-1])
        limpiar_seleccion(self.tabla)

    def seleccionar(self, _evento=None):
        sel = self.tabla.selection()
        if not sel:
            return
        u = buscar(self.datos.usuarios, sel[0], "id_usuario")
        self.poner_id(u["id_usuario"], False)
        for clave, valor in (("Nombre", u["nombre"]), ("Usuario", u["usuario"])):
            self.entries[clave].delete(0, tk.END)
            self.entries[clave].insert(0, valor)
        self.entries["Contraseña"].delete(0, tk.END)
        self.combo_rol.set(u["rol"])


# ======================= PRODUCTOS =======================
class ProductosView(tk.Frame):
    CATEGORIAS = ["Comida", "Comida rapida", "Bebida", "Dulces"]

    def __init__(self, parent, datos):
        super().__init__(parent, bg="white")
        self.datos = datos
        crear_titulo(self, "Gestión de productos")

        form = tk.LabelFrame(self, text="Datos del producto", padx=10, pady=10)
        form.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        self.entries = {}
        for i, texto in enumerate(["Código", "Nombre"]):
            tk.Label(form, text=texto).grid(row=i, column=0, sticky="w", pady=8)
            entry = tk.Entry(form, width=26)
            entry.grid(row=i, column=1, pady=8, padx=10)
            self.entries[texto] = entry

        tk.Label(form, text="Categoría").grid(row=2, column=0, sticky="w", pady=8)
        # Se puede elegir de la lista o escribir una categoría nueva
        self.combo_cat = ttk.Combobox(form, values=self.CATEGORIAS, width=23)
        self.combo_cat.set(self.CATEGORIAS[0])
        self.combo_cat.grid(row=2, column=1, pady=8, padx=10)

        for i, texto in enumerate(["Precio", "Stock"], start=3):
            tk.Label(form, text=texto).grid(row=i, column=0, sticky="w", pady=8)
            entry = tk.Entry(form, width=26)
            entry.grid(row=i, column=1, pady=8, padx=10)
            self.entries[texto] = entry

        crear_botones(form, [
            ("+  Registrar", "#2563eb", self.registrar),
            ("✏  Actualizar", "#3b82f6", self.actualizar),
            ("🗑  Eliminar", "#dc2626", self.eliminar),
            ("🧹  Limpiar", "#1e293b", self.limpiar),
        ], 5)

        marco = tk.LabelFrame(self, text="Productos del restaurante", padx=10, pady=10)
        marco.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.tabla = crear_tabla(marco, [
            ("codigo", "Código", 65, "center"), ("nombre", "Nombre", 150, "w"),
            ("categoria", "Categoría", 105, "center"), ("precio", "Precio", 65, "e"),
            ("stock", "Stock", 55, "center")])
        self.tabla.bind("<<TreeviewSelect>>", self.seleccionar)

    def refresh(self):
        self.datos.guardar()
        usadas = [p["categoria"] for p in self.datos.productos]
        extras = sorted(set(usadas) - set(self.CATEGORIAS))
        self.combo_cat["values"] = self.CATEGORIAS + extras
        self.tabla.delete(*self.tabla.get_children())
        for p in self.datos.productos:
            self.tabla.insert("", tk.END, iid=p["codigo"], values=(
                p["codigo"], p["nombre"], p["categoria"], dinero(p["precio"]), p["stock"]))

    def poner_codigo(self, texto, editable):
        e = self.entries["Código"]
        e.config(state="normal")
        e.delete(0, tk.END)
        e.insert(0, texto)
        if not editable:  # el código de un producto existente no se cambia
            e.config(state="disabled")

    def leer_formulario(self):
        """Devuelve (nombre, categoria, precio, stock) o None si hay error."""
        nombre = self.entries["Nombre"].get().strip()
        categoria = self.combo_cat.get().strip()
        if not nombre or not categoria:
            messagebox.showwarning("Datos incompletos", "Nombre y categoría son obligatorios.")
            return None
        try:
            precio = float(self.entries["Precio"].get().strip().replace(",", "."))
            stock = int(self.entries["Stock"].get().strip())
            if precio < 0 or stock < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Precio debe ser un número y Stock un entero (ambos 0 o más).")
            return None
        return nombre, categoria, precio, stock

    def registrar(self):
        codigo = self.entries["Código"].get().strip()
        if not codigo:
            messagebox.showwarning("Datos incompletos", "Escribe el código del producto.")
            return
        if any(p["codigo"].lower() == codigo.lower() for p in self.datos.productos):
            messagebox.showerror("Error", f"Ya existe un producto con el código {codigo}.")
            return
        datos = self.leer_formulario()
        if not datos:
            return
        nombre, categoria, precio, stock = datos
        self.datos.productos.append({
            "codigo": codigo, "nombre": nombre, "categoria": categoria,
            "precio": precio, "stock": stock})
        self.limpiar()
        self.refresh()

    def actualizar(self):
        sel = self.tabla.selection()
        if not sel:
            messagebox.showwarning("Actualizar", "Selecciona un producto de la tabla.")
            return
        datos = self.leer_formulario()
        if not datos:
            return
        p = buscar(self.datos.productos, sel[0], "codigo")
        p["nombre"], p["categoria"], p["precio"], p["stock"] = datos
        self.limpiar()
        self.refresh()

    def eliminar(self):
        sel = self.tabla.selection()
        if not sel:
            messagebox.showwarning("Eliminar", "Selecciona un producto de la tabla.")
            return
        p = buscar(self.datos.productos, sel[0], "codigo")
        if messagebox.askyesno("Eliminar", f"¿Eliminar el producto {p['nombre']}?"):
            self.datos.productos.remove(p)
            self.limpiar()
            self.refresh()

    def limpiar(self):
        for clave in ("Nombre", "Precio", "Stock"):
            self.entries[clave].delete(0, tk.END)
        self.poner_codigo("", True)
        self.combo_cat.set(self.CATEGORIAS[0])
        limpiar_seleccion(self.tabla)

    def seleccionar(self, _evento=None):
        sel = self.tabla.selection()
        if not sel:
            return
        p = buscar(self.datos.productos, sel[0], "codigo")
        self.poner_codigo(p["codigo"], False)
        for clave, valor in (("Nombre", p["nombre"]), ("Precio", f"{p['precio']:.2f}"),
                             ("Stock", str(p["stock"]))):
            self.entries[clave].delete(0, tk.END)
            self.entries[clave].insert(0, valor)
        self.combo_cat.set(p["categoria"])


# ======================= VENTAS =======================
class VentasView(tk.Frame):
    def __init__(self, parent, datos, usuario_actual):
        super().__init__(parent, bg="white")
        self.datos = datos
        self.nombre_vendedor = self.obtener_nombre(usuario_actual)
        self.id_vendedor = self.obtener_id(usuario_actual)
        crear_titulo(self, "Gestión de ventas")

        form = tk.LabelFrame(self, text="Nueva venta", padx=10, pady=10)
        form.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        tk.Label(form, text="Producto").grid(row=0, column=0, sticky="w", pady=8)
        self.combo_prod = ttk.Combobox(form, state="readonly", width=28)
        self.combo_prod.grid(row=0, column=1, pady=8, padx=10)
        self.combo_prod.bind("<<ComboboxSelected>>", self.calcular_total)

        tk.Label(form, text="Cantidad").grid(row=1, column=0, sticky="w", pady=8)
        self.entry_cant = tk.Entry(form, width=30)
        self.entry_cant.insert(0, "1")
        self.entry_cant.grid(row=1, column=1, pady=8, padx=10)
        self.entry_cant.bind("<KeyRelease>", self.calcular_total)

        self.lbl_total = tk.Label(form, text="Total: $0.00", font=("Arial", 14, "bold"))
        self.lbl_total.grid(row=2, column=0, columnspan=2, sticky="w", pady=(10, 15))

        crear_botones(form, [
            ("💰  Registrar venta", "#16a34a", self.registrar),
            ("↩  Anular venta", "#dc2626", self.anular),
            ("🧹  Limpiar", "#1e293b", self.limpiar),
        ], 3)

        marco = tk.LabelFrame(self, text="Ventas registradas", padx=10, pady=10)
        marco.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.lbl_dia = tk.Label(marco, text="", font=("Arial", 12, "bold"), anchor="e")
        self.lbl_dia.pack(side=tk.BOTTOM, fill=tk.X, pady=(8, 0))
        self.tabla = crear_tabla(marco, [
            ("id", "ID", 55, "center"), ("fecha", "Fecha", 115, "center"),
            ("producto", "Producto", 140, "w"), ("cantidad", "Cant.", 45, "center"),
            ("total", "Total", 70, "e")])

    @staticmethod
    def obtener_id(usuario):
        if isinstance(usuario, dict):
            return str(usuario.get("id_usuario", ""))
        return str(getattr(usuario, "id_usuario", ""))

    @staticmethod
    def obtener_nombre(usuario):
        if isinstance(usuario, dict):
            return usuario.get("nombre", "Usuario")
        return getattr(usuario, "nombre", str(usuario))

    def refresh(self):
        self.datos.guardar()
        self.combo_prod["values"] = [
            f"{p['codigo']} - {p['nombre']} (stock {p['stock']})" for p in self.datos.productos]
        self.tabla.delete(*self.tabla.get_children())
        for v in reversed(self.datos.ventas):
            self.tabla.insert("", tk.END, iid=v["id"], values=(
                v["id"], v["fecha"], v["producto"], v["cantidad"], dinero(v["total"])))
        hoy = datetime.now().strftime("%Y-%m-%d")
        total_hoy = sum(v["total"] for v in self.datos.ventas if v["fecha"].startswith(hoy))
        self.lbl_dia.config(text=f"Total vendido hoy: {dinero(total_hoy)}")

    def producto_elegido(self):
        texto = self.combo_prod.get()
        if not texto:
            return None
        return buscar(self.datos.productos, texto.split(" - ")[0], "codigo")

    def cantidad(self):
        try:
            n = int(self.entry_cant.get().strip())
            return n if n > 0 else None
        except ValueError:
            return None

    def calcular_total(self, _evento=None):
        p, n = self.producto_elegido(), self.cantidad()
        total = p["precio"] * n if p and n else 0
        self.lbl_total.config(text=f"Total: {dinero(total)}")

    def registrar(self):
        p, n = self.producto_elegido(), self.cantidad()
        if not p:
            messagebox.showwarning("Venta", "Selecciona un producto.")
            return
        if not n:
            messagebox.showerror("Venta", "La cantidad debe ser un entero mayor a 0.")
            return
        if n > p["stock"]:
            messagebox.showerror("Venta", f"Stock insuficiente: quedan {p['stock']} de {p['nombre']}.")
            return
        p["stock"] -= n
        self.datos.ventas.append({
            "id": siguiente_id("V", self.datos.ventas),
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "producto_id": p["codigo"], "producto": p["nombre"], "cantidad": n,
            "total": p["precio"] * n, "vendedor": self.nombre_vendedor,
            "vendedor_id": self.id_vendedor})
        self.limpiar()
        self.refresh()

    def anular(self):
        sel = self.tabla.selection()
        if not sel:
            messagebox.showwarning("Anular", "Selecciona una venta de la tabla.")
            return
        v = buscar(self.datos.ventas, sel[0])
        if messagebox.askyesno("Anular", f"¿Anular la venta {v['id']}? Se devolverá el stock."):
            p = buscar(self.datos.productos, v["producto_id"], "codigo")
            if p:
                p["stock"] += v["cantidad"]
            self.datos.ventas.remove(v)
            self.refresh()

    def limpiar(self):
        self.combo_prod.set("")
        self.entry_cant.delete(0, tk.END)
        self.entry_cant.insert(0, "1")
        self.lbl_total.config(text="Total: $0.00")
        limpiar_seleccion(self.tabla)


# ======================= VENTANA PRINCIPAL =======================
class MainView(tk.Frame):
    """Interfaz principal. main.py la crea con 4 argumentos y la empaqueta."""

    def __init__(self, parent, servicio, usuario_actual, on_logout):
        super().__init__(parent)  # sin self.pack(): lo hace cambiar_vista()
        self.servicio = servicio
        self.usuario_actual = usuario_actual
        self.on_logout = on_logout
        self.datos = Datos(servicio)

        if isinstance(usuario_actual, dict):
            nombre = usuario_actual.get("nombre", "Usuario")
        else:
            nombre = getattr(usuario_actual, "nombre", str(usuario_actual))

        # ---------- Menú izquierdo ----------
        menu = tk.Frame(self, bg=COLOR_MENU, width=220)
        menu.pack(side=tk.LEFT, fill=tk.Y)
        menu.pack_propagate(False)

        tk.Label(menu, text=TITULO_APP, fg="white", bg=COLOR_MENU,
                 font=("Arial", 18, "bold")).pack(pady=20)
        tk.Label(menu, text=nombre, fg="lightgray", bg=COLOR_MENU,
                 font=("Arial", 10)).pack(pady=(0, 30))

        # ---------- Área de contenido ----------
        self.contenedor = tk.Frame(self, bg="white")
        self.contenedor.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.vistas = {
            "inicio": InicioView(self.contenedor, self.datos),
            "usuarios": UsuariosView(self.contenedor, self.datos),
            "productos": ProductosView(self.contenedor, self.datos),
            "ventas": VentasView(self.contenedor, self.datos, usuario_actual),
        }
        self.vista_actual = None

        # ---------- Botones del menú ----------
        self.botones = {}
        for clave, texto in [("inicio", "  Inicio"), ("usuarios", "  Usuarios"),
                             ("productos", "  Productos"), ("ventas", "  Ventas")]:
            boton = tk.Button(menu, text=texto, bg=COLOR_BOTON, fg="white",
                              font=("Arial", 12, "bold"), padx=10, pady=5,
                              relief="raised", width=12,
                              command=lambda c=clave: self.mostrar(c))
            boton.pack(pady=2)
            self.botones[clave] = boton

        tk.Button(menu, text=" Cerrar sesión", bg="#ed2642", fg="white",
                  font=("Arial", 11), pady=12, command=self.cerrar_sesion
                  ).pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        self.mostrar("inicio")

    def mostrar(self, clave):
        if self.vista_actual is not None:
            self.vista_actual.pack_forget()
        self.vista_actual = self.vistas[clave]
        self.vista_actual.pack(fill=tk.BOTH, expand=True)
        for k, boton in self.botones.items():
            boton.config(bg=COLOR_ACTIVO if k == clave else COLOR_BOTON)
        try:
            self.vista_actual.refresh()
        except Exception as error:
            messagebox.showerror("Error al abrir la sección",
                                 f"{type(error).__name__}: {error}")

    def cerrar_sesion(self):
        self.on_logout()