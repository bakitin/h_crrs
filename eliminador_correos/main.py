import logging
from configuracion import Configuracion
from cliente_imap import ClienteImap
from filtro import FiltroBorrado
from servicio_borrado import ServicioBorrado


# ----CONFIG----
configuracion = Configuracion(".env")
cuentas = configuracion.leer_cuentas()

# ----LOGS----
logging.basicConfig(
    level=logging.INFO, #registra los mensajes de nivel INFO y superiores.
    format="%(asctime)s %(levelname)s %(message)s", #cómo se ve cada línea. %(asctime)s es la fecha y hora, %(levelname)s el nivel (INFO, ERROR) y %(message)s tu texto.
    handlers=[
        logging.StreamHandler(),
    ], #a dónde va cada mensaje. FileHandler escribe en el archivo y StreamHandler en la pantalla. Con los dos, una sola línea de código escribe en ambos lugares.
)

# ----FILTRO DE BORRADO----
filtro = FiltroBorrado(configuracion.remitentes,configuracion.asuntos,configuracion.desde,configuracion.hasta)
criterios = filtro.criterios_imap()
logging.info(f"Criterios IMAP: {criterios}")


# ----IMAP----
cliente = ClienteImap(configuracion.host, configuracion.puerto)


# ----PROGRAMA----
servicio = ServicioBorrado(cliente, criterios)
servicio.borrar_todas(cuentas)
