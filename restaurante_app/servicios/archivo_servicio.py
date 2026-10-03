import json
from pathlib import Path

class ArchivoServicio:
    def __init__(self, carpeta_datos):
        self.carpeta = Path(carpeta_datos)
        self.carpeta.mkdir(exist_ok=True)

    def leer_archivo(self, nombre_archivo):
        """Lee y devuelve el contenido de un archivo JSON"""
        ruta = self.carpeta / nombre_archivo
        if not ruta.exists():
            return []
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)

    def escribir_archivo(self, nombre_archivo, datos):
        """Escribe datos en un archivo JSON"""
        ruta = self.carpeta / nombre_archivo
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=4)