class Usuario:
    ROLES_PERMITIDOS = ("Administrador", "Empleado", "Cliente")

    def __init__(self, id_usuario, nombre, usuario, contrasena, rol):
        self.id_usuario = id_usuario
        self.nombre = nombre
        self.usuario = usuario
        self.contrasena = contrasena
        self.rol = rol

    @staticmethod
    def validar_texto(valor, campo):
        # Reutiliza una validacion basica para datos obligatorios.
        if not valor or not valor.strip():
            raise ValueError(f"El campo {campo} no puede estar vacio.")
        return valor.strip()

    @property
    def id_usuario(self):
        return self._id_usuario

    @id_usuario.setter
    def id_usuario(self, valor):
        # Permite numeros o textos como identificador
        if isinstance(valor, int):
            self._id_usuario = valor
        else:
            self._id_usuario = self.validar_texto(valor, "id_usuario")

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        self._nombre = self.validar_texto(valor, "nombre")

    @property
    def usuario(self):
        return self._usuario

    @usuario.setter
    def usuario(self, valor):
        self._usuario = self.validar_texto(valor, "usuario")

    @property
    def contrasena(self):
        return self._contrasena

    @contrasena.setter
    def contrasena(self, valor):
        self._contrasena = self.validar_texto(valor, "contrasena")

    @property
    def rol(self):
        return self._rol

    @rol.setter
    def rol(self, valor):
        rol_validado = self.validar_texto(valor, "rol")
        if rol_validado not in self.ROLES_PERMITIDOS:
            raise ValueError("El rol seleccionado no es valido.")
        self._rol = rol_validado

    def to_dict(self):
        return {
            "id_usuario": self.id_usuario,
            "nombre": self.nombre,
            "usuario": self.usuario,
            "contrasena": self.contrasena,
            "rol": self.rol
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            d.get("id_usuario", d.get("identificador", 1)),
            d["nombre"],
            d["usuario"],
            d["contrasena"],
            d["rol"]
        )