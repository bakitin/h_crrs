import logging
from configuracion import Configuracion
from cliente_imap import ClienteImap
from almacen import Almacen
from servicio_backup import ServicioBackup
from analizador import AnalizadorCorreo

# ----CONFIG----
configuracion = Configuracion(".env")
cuentas = configuracion.leer_cuentas()

# ----LOGS----
logging.basicConfig(
    level=logging.INFO, #registra los mensajes de nivel INFO y superiores.
    format="%(asctime)s %(levelname)s %(message)s", #cómo se ve cada línea. %(asctime)s es la fecha y hora, %(levelname)s el nivel (INFO, ERROR) y %(message)s tu texto.
    handlers=[
        logging.FileHandler(configuracion.destino / "backup.log", encoding="utf-8"),
        logging.StreamHandler(),
    ], #a dónde va cada mensaje. FileHandler escribe en el archivo y StreamHandler en la pantalla. Con los dos, una sola línea de código escribe en ambos lugares.
)

# ----IMAP----
cliente = ClienteImap(configuracion.host, puerto = configuracion.puerto)

# ----ALMACEN----
almacen = Almacen(configuracion.destino)

# ----ANALIZADOR----
analizador = AnalizadorCorreo()


# ----PROGRAMA----
servicio = ServicioBackup(cliente, almacen, analizador, configuracion.extraer_adjuntos)
servicio.respaldar_todas(cuentas)



