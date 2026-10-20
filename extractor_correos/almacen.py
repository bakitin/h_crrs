"""Almacen: nombres de carpeta seguros para Windows y escritura a disco."""
import time
import os
class Almacen:
    def __init__(self, destino):                                   # guarda la carpeta raíz (Path)
        self.destino = destino
        self.nombres_reservados_windows = ["CON","PRN","AUX","NUL","COM1","COM2","COM3","COM4","COM5","COM6","COM7","COM8","COM9","LPT1","LPT2","LPT3","LPT4","LPT5","LPT6","LPT7","LPT8","LPT9"]

    def guardar_eml(self, cuenta, carpeta, uid, contenido, fecha, asunto, cuerpo, adjuntos):        # devuelve la ruta del archivo guardado

        asunto_seguro = self._nombre_seguro(asunto)[:50]

        fecha_texto=time.strftime("%Y-%m-%d_%H%M", fecha)

        #-------------------------------------

        nombre_carpeta_buzon = carpeta.strip('"')

        ruta_carpeta_buzon = self.destino/self._nombre_windows(cuenta)/nombre_carpeta_buzon

        ruta_carpeta_buzon.mkdir(parents=True, exist_ok=True)

        #-------------------------------------

        nombre_carpeta_correo = f"{fecha_texto}_uid{uid}_{asunto_seguro}"

        ruta_carpeta_correo = self.destino/self._nombre_windows(cuenta)/nombre_carpeta_buzon/nombre_carpeta_correo

        ruta_carpeta_correo.mkdir(parents=True, exist_ok=True)

        #-------------------------------------

        nombre_archivo = f"{uid}.eml"

        (ruta_carpeta_correo/nombre_archivo).write_bytes(contenido)

        #-------------------------------------
        
        nombre_cuerpo = "cuerpo.txt"

        (ruta_carpeta_correo/nombre_cuerpo).write_text(cuerpo, encoding="utf-8")


        #-------------------------------------

        numero = 0

        for nombre_adjunto, datos in adjuntos:

            numero += 1

            nombre = self._nombre_seguro(nombre_adjunto)

            nombre_carpeta_adjuntos = "Adjuntos"
                        
            ruta_carpeta_adjuntos = self.destino/self._nombre_windows(cuenta)/nombre_carpeta_buzon/nombre_carpeta_correo/nombre_carpeta_adjuntos
    
            ruta_carpeta_adjuntos.mkdir(parents=True, exist_ok=True)

            (ruta_carpeta_adjuntos/f"{numero}_{nombre}").write_bytes(datos)

        #-------------------------------------

        segundos = time.mktime(fecha)

        os.utime(ruta_carpeta_correo, (segundos, segundos))

        #-------------------------------------

        return fecha_texto , nombre_archivo, nombre_carpeta_buzon

    def _nombre_seguro(self, asunto):
        if not asunto:
            return "sin-asunto"
        else:
            for caracter in ':?/\\*<>|" ':
                asunto = asunto.replace(caracter, "-")
            return asunto


    def existe(self, cuenta, carpeta, uid):

        nombre_carpeta_buzon = carpeta.strip('"')

        ruta = self.destino/self._nombre_windows(cuenta)/nombre_carpeta_buzon

        archivos = list(ruta.glob(f"*_uid{uid}_*/{uid}.eml"))

        return bool(archivos)

    def _nombre_windows(self, nombre):
        if nombre.split(".")[0].upper() in self.nombres_reservados_windows :
            return "_"+nombre
        else:
            return nombre
