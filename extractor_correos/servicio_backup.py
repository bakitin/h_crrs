"""ServicioBackup: orquesta cuentas, carpetas y mensajes; aísla errores por mensaje."""
import logging
class ServicioBackup:
    def __init__(self, cliente, almacen, analizador, extraer_adjuntos):
        self.cliente = cliente
        self.almacen = almacen
        self.analizador = analizador
        self.extraer_adjuntos = extraer_adjuntos

    def respaldar_todas(self, cuentas):            # recorre las cuentas, con try por cuenta
        for cuenta in cuentas:
            try:
                self.respaldar_cuenta(cuenta["correo"],cuenta["clave"])

            except Exception as error:
                logging.error(f"Error en la cuenta {cuenta['correo']} | {error}")

    def respaldar_cuenta(self, usuario, clave):    # conectar, carpetas, correos, desconectar

        logging.info(f"Entrando a: {usuario} ...")

        self.cliente.conectar(usuario,clave)

        logging.info(f"Sesion iniciada en: {usuario}")

        carpetas = self.cliente.listar_carpetas()

        logging.info("Se inicia backup de correos, espere... Esto tomara tiempo.")
        for carpeta in carpetas:
            uids = self.cliente.listar_uids(carpeta)
            
            for uid in uids:
                try:
                    if self.almacen.existe(usuario,carpeta,uid):
                        logging.info(f"Ya existe, se salta: {usuario} | {carpeta} | uid {uid}")
                        continue
                    
                    fecha, contenido = self.cliente.traer_correo(uid)
                    asunto = self.analizador.leer_asunto(contenido)
                    cuerpo = self.analizador.leer_cuerpo(contenido)
                    adjuntos = self.analizador.leer_adjuntos(contenido)
                    if not self.extraer_adjuntos:
                        adjuntos = []
                    fecha_texto, nombre_archivo, carpeta_guardada = self.almacen.guardar_eml(usuario, carpeta, uid, contenido, fecha, asunto, cuerpo, adjuntos)

                    logging.info(f"Correo guardado: {usuario} | {fecha_texto} | uid {uid} | {carpeta_guardada}")

                except Exception as error:
                    logging.error(f"Error en el correo: {usuario} | {carpeta} | uid {uid} | {error}")


        logging.info(f"Proceso finalizado, cerrando sesion de: {usuario}")
        logging.info("---------------------------------------------------")
        self.cliente.desconectar()
