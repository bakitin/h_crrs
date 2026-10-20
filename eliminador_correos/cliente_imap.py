"""ClienteImap: conexión, listado de carpetas y descarga de mensajes en solo lectura."""
from imaplib import IMAP4_SSL, Internaldate2tuple
class ClienteImap:
    def __init__(self, host, puerto):        # solo guarda host y puerto
        self.host = host
        self.puerto = puerto

    def conectar(self, usuario, clave):      # crea self.imap y hace login
        self.imap = IMAP4_SSL(self.host, self.puerto)
        self.imap.login(usuario,clave)

    def listar_carpetas(self):               # devuelve ['INBOX', '"Elementos enviados"', ...]
        estado, lineas = self.imap.list()
        if estado != "OK":
            raise RuntimeError(f"El servidor respondio {estado}: {lineas}")
        carpetas=[]
        for linea in lineas:
            linea_texto = linea.decode()
            partes = linea_texto.rpartition('"/"')
            nombre = partes[2].strip()
            carpetas.append(nombre)
        return carpetas

    def buscar_uids(self,carpeta, criterios):
        estado, datos = self.imap.select(carpeta, readonly=True)
        if estado != "OK":
            raise RuntimeError(f"El servidor respondio {estado}: {datos}")
        
        estado,respuesta = self.imap.uid("SEARCH", None, *criterios)
        if estado != "OK":
            raise RuntimeError(f"El servidor respondio {estado}: {respuesta}")
        
        uids_bytes = respuesta[0].split()
        uids = []
        for uid_bytes in uids_bytes:
            uid = uid_bytes.decode()
            uids.append(uid)
        return uids

    
    def marcar_borrados(self, carpeta, uids):
        if not uids:
            return ("La lista de UIDS viene vacia, se corta la asignacion de correos a eliminar")
        cadena = ",".join(uids)
        estado, datos = self.imap.select(carpeta, readonly=False)
        if estado != "OK":
            raise RuntimeError(f"No se encontro la carpeta a la hora de intentar marcar los correos a eliminar, el servidor respondio: {estado}: {datos}")
        estado, datos = self.imap.uid("STORE", cadena, "+FLAGS", r"(\Deleted)")
        if estado != "OK":
            raise RuntimeError(f"El servidor respondió {estado}: {datos}")
        return("Todo salio con exito y se marcaron los correos a eliminar")


    def expulsar_borrados(self):
        estado, datos = self.imap.expunge()
        if estado != "OK":
            raise RuntimeError(f"El servidor respondió {estado}: {datos}")
        return("La expulsion termino correctamente")


    def desconectar(self):                   # logout
        self.imap.logout()

    
    