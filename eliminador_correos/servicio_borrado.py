
import logging
class ServicioBorrado:

    def __init__(self, cliente, criterios):
        self.cliente = cliente
        self.criterios = criterios

    def informar(self, mensaje):
        separador = "-" * 60
        logging.info(separador)
        logging.info(mensaje)
        logging.info(separador)

    def borrar_carpeta(self,carpeta):
        self.informar(f"Buscando coincidencias en: {carpeta}")
        uids = self.cliente.buscar_uids(carpeta, self.criterios)
        if not uids:
            self.informar(f"No se encontraron coincidencias en: {carpeta}")
            return
        self.informar(f"UIDs encontrados en {carpeta}: {uids}")
        self.cliente.marcar_borrados(carpeta, uids)
        self.informar(f"Se marcaron {len(uids)} correos en: {carpeta}")
        self.cliente.expulsar_borrados()
        self.informar(f"Se eliminaron {len(uids)} correos de: {carpeta}")

    def borrar_carpetas(self):
        carpetas = self.cliente.listar_carpetas()
        for carpeta in carpetas:
            if carpeta == '"[Gmail]"':
                continue
            self.borrar_carpeta(carpeta)

    def borrar_cuenta(self, usuario, clave):
        self.informar(f"Procesando cuenta: {usuario}")
        self.cliente.conectar(usuario,clave)
        try:
            self.borrar_carpetas()
        finally: #siempre se ejecuta, no importa si ocurre un error en el try
            self.informar(f"Cerrando sesión: {usuario}")
            self.cliente.desconectar()
        self.informar(f"Cuenta finalizada: {usuario}")

    def borrar_todas(self, cuentas):
        for cuenta in cuentas:
            try:
                self.borrar_cuenta(cuenta["correo"],cuenta["clave"])

            except Exception as error:
                logging.error(f"Error en la cuenta {cuenta['correo']} | {error}")