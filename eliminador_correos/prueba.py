import logging
from configuracion import Configuracion
from cliente_imap import ClienteImap
from filtro import FiltroBorrado
from servicio_borrado import ServicioBorrado


# ----CONFIG----
configuracion = Configuracion(".env")
cuentas = configuracion.leer_cuentas()

# ----IMAP----
cliente = ClienteImap(configuracion.host, configuracion.puerto)

cliente.conectar("daftpunki308@gmail.com","oixwtraoqkpkhnen")

print(cliente.listar_carpetas())
