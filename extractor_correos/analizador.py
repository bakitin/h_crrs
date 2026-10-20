"""AnalizadorCorreo: convierte bytes .eml en asunto, cuerpo de texto y adjuntos."""
from email import message_from_bytes
from email.policy import default
from pathlib import Path
class AnalizadorCorreo:

    def leer_asunto(self, contenido):      # recibe los bytes del .eml, devuelve el asunto (str)
        mensaje = message_from_bytes(contenido, policy=default)
        return mensaje["Subject"]

    def leer_cuerpo(self, contenido):
        mensaje = message_from_bytes(contenido, policy=default)
        try:
            parte = mensaje.get_body(preferencelist=("plain", "html"))
            if not parte:
                return ""
            else:
                return parte.get_content()
        except Exception as error:
            return f"(No se pudo leer el cuerpo: {error})"


    def leer_adjuntos(self, contenido):
        mensaje = message_from_bytes(contenido, policy=default)
        try:
            adjuntos = []
            partes = mensaje.walk()
            for parte in partes:

                nombre_adjunto = parte.get_filename()
                datos = parte.get_payload(decode=True)

                if nombre_adjunto:
                    adjuntos.append((nombre_adjunto, datos))
            return adjuntos

        except Exception:
            return adjuntos