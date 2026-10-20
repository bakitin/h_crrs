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
        carpetas=[]
        for linea in lineas:
            linea_texto = linea.decode()
            partes = linea_texto.rpartition('"/"')
            nombre = partes[2].strip()
            carpetas.append(nombre)
        return carpetas

    def listar_uids(self, carpeta):          # select + search, devuelve ['8','9', ...]
        self.imap.select(carpeta, readonly=True)
        estado,respuesta = self.imap.uid("SEARCH", None, "ALL")
        uids_bytes = respuesta[0].split()
        uids = []
        for uid_bytes in uids_bytes:
            uid = uid_bytes.decode()
            uids.append(uid)
        return uids

    def traer_correo(self, uid):             # devuelve los bytes del .eml y la fecha
        estado,respuesta = self.imap.uid("FETCH", uid, "(INTERNALDATE BODY.PEEK[])")
        etiqueta = respuesta[0][0]
        contenido = respuesta[0][1]
        fecha = Internaldate2tuple(etiqueta)
        return fecha, contenido
    
    def desconectar(self):                   # logout
        self.imap.logout()