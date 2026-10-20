"""Configuracion: lee .env y el CSV de cuentas, valida y entrega valores tipados."""
from pathlib import Path
import csv
class Configuracion:
    def __init__(self, ruta_env):
        self.cargar_env(ruta_env)

    def leer_cuentas(self):
        with open(self.ruta_cuentas, encoding="utf-8-sig", newline="") as archivo:
            lector = csv.DictReader(archivo)
            cuentas = list(lector)
            return cuentas

    def cargar_env(self, ruta_env):
        texto = Path(ruta_env).read_text(encoding="utf-8")
        valores = {}
        for linea in texto.splitlines():
            partes = linea.partition("=")#Busca un separador que tú le indiques y corta el texto la primera vez que lo encuentra. Siempre te devolverá el texto de la izquierda, el separador mismo, y el texto de la derecha.
                
            nombre = partes[0].strip()#Borra los espacios en blanco, tabulaciones o saltos de línea (\n) que estén al inicio y al final de un texto. No toca los espacios del centro. También puedes usarlo para quitar caracteres específicos de las orillas.
                
            valor = partes[2].strip()

            valores[nombre] = valor

        self.host = valores["IMAP_HOST"]
        self.extraer_adjuntos = valores["EXTRAER_ADJUNTOS"].lower() == "si"
        self.puerto = int(valores["IMAP_PUERTO"])
        self.destino = Path(valores["DESTINO"])
        self.ruta_cuentas = Path(valores["CUENTAS_CSV"])
        