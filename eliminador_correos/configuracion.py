"""Configuracion: lee .env y el CSV de cuentas, valida y entrega valores tipados."""
from pathlib import Path
from datetime import date
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
        self.puerto = int(valores["IMAP_PUERTO"])
        self.ruta_cuentas = Path(valores["CUENTAS_CSV"])

        #--------------------LEER--------------------
        remitentes_crud = valores.get("BORRAR_REMITENTE","")
        asuntos_crud = valores.get("BORRAR_ASUNTO","")
        desde_crud = valores.get("BORRAR_DESDE","")
        hasta_crud = valores.get("BORRAR_HASTA","")
        #--------------------------------------------

        #-----------LIMPIAR Y CONVERTIR--------------------
        remitentes = self._limpiar_listas(remitentes_crud)
        asuntos = self._limpiar_listas(asuntos_crud)
        desde, hasta = self._configuracion_fechas(desde_crud, hasta_crud)
        #--------------------------------------------------

        #-----------VALIDAR--------------------------------
        if not self._validar_datos(remitentes, asuntos, desde, hasta):
            raise ValueError("Debe de dar por lo menos un parametro para elminar")
        self.remitentes = remitentes
        self.asuntos = asuntos
        self.desde = desde
        self.hasta = hasta
        #--------------------------------------------------

    def _limpiar_listas(self, lista):
        lista_limpia = []
        dato_separado= lista.split(";")
        for dato in dato_separado:
            dato_sinespacios = dato.strip()
            if dato_sinespacios:
                lista_limpia.append(dato_sinespacios)
        return lista_limpia


    def _configuracion_fechas(self, desde, hasta):
        desde_format = date.fromisoformat(desde) if desde else None
        hasta_format = date.fromisoformat(hasta) if hasta else None
        if desde_format and hasta_format:
            if hasta_format < desde_format:
                raise ValueError("Las fechas no tienen sentido")
            return desde_format,hasta_format
        return desde_format, hasta_format


    def _validar_datos(self ,remitentes, asuntos, desde, hasta):
        if remitentes or asuntos or desde or hasta:
            return True
        else:
            return False