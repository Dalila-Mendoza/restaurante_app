class Venta:
    def __init__(self, id_venta, usuario, producto, fecha):
        self.id_venta = id_venta
        self.usuario = usuario
        self.producto = producto
        self.fecha = fecha

    @staticmethod
    def validar_texto(valor, campo):
        if not valor or not valor.strip():
            raise ValueError(f"El campo {campo} no puede estar vacio.")
        return valor.strip()

    @property
    def id_venta(self):
        return self._id_venta

    @id_venta.setter
    def id_venta(self, valor):
        if isinstance(valor, int):
            self._id_venta = valor
        else:
            self._id_venta = self.validar_texto(valor, "id_venta")

    @property
    def usuario(self):
        return self._usuario

    @usuario.setter
    def usuario(self, valor):
        self._usuario = self.validar_texto(valor, "usuario")

    @property
    def producto(self):
        return self._producto

    @producto.setter
    def producto(self, valor):
        self._producto = self.validar_texto(valor, "producto")

    @property
    def fecha(self):
        return self._fecha

    @fecha.setter
    def fecha(self, valor):
        self._fecha = self.validar_texto(valor, "fecha")

    def to_dict(self):
        return {
            "id_venta": self.id_venta,
            "usuario": self.usuario,
            "producto": self.producto,
            "fecha": self.fecha
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            d.get("id_venta", d.get("identificador", 1)),
            d.get("usuario", d.get("usuario_id", "")),
            d.get("producto", d.get("libro_codigo", "")),
            d["fecha"]
        )