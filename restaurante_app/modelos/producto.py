class Producto:
    def __init__(self, codigo, nombre, categoria, precio, stock):
        self.codigo = codigo
        self.nombre = nombre
        self.categoria = categoria
        self.precio = precio
        self.stock = stock

    @staticmethod
    def validar_texto(valor, campo):
        # Reutiliza una validacion basica para datos obligatorios.
        if not valor or not valor.strip():
            raise ValueError(f"El campo {campo} no puede estar vacio.")
        return valor.strip()

    @property
    def codigo(self):
        return self._codigo

    @codigo.setter
    def codigo(self, valor):
        self._codigo = self.validar_texto(valor, "codigo")

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        self._nombre = self.validar_texto(valor, "nombre")

    @property
    def categoria(self):
        return self._categoria

    @categoria.setter
    def categoria(self, valor):
        self._categoria = self.validar_texto(valor, "categoria")

    @property
    def precio(self):
        return self._precio

    @precio.setter
    def precio(self, valor):
        if not isinstance(valor, (int, float)) or valor <= 0:
            raise ValueError("El precio debe ser un numero mayor a cero.")
        self._precio = valor

    @property
    def stock(self):
        return self._stock

    @stock.setter
    def stock(self, valor):
        if not isinstance(valor, int) or valor < 0:
            raise ValueError("El stock debe ser un numero entero no negativo.")
        self._stock = valor

    def to_dict(self):
        return {
            "codigo": self.codigo,
            "nombre": self.nombre,
            "categoria": self.categoria,
            "precio": self.precio,
            "stock": self.stock
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            d["codigo"],
            d["nombre"],
            d["categoria"],
            d["precio"],
            d["stock"]
        )