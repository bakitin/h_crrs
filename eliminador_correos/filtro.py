from datetime import date, timedelta

class FiltroBorrado:
    def __init__(self, remitentes, asuntos, desde, hasta):
        self.remitentes = remitentes
        self.asuntos = asuntos
        self.desde = desde
        self.hasta = hasta

    

    def _frases_remitentes(self):
        frases = []
        for remitente in self.remitentes:
            frases.append(["FROM", f'"{remitente}"'])
        
        return frases

    def _frases_asuntos(self):
        frases = []
        for asunto in self.asuntos:
            frases.append(["SUBJECT", f'"{asunto}"'])
        
        return frases

    def _todas_las_frases(self):
        remitentes = self._frases_remitentes()
        asuntos = self._frases_asuntos()
        frases = (remitentes+asuntos)
        return frases

    def _encadenar_con_or(self):
        resultado =[]
        frases = self._todas_las_frases()
        if not frases:
            return resultado
        
        for frase in frases[:-1]:
            resultado.append("OR")
            resultado.extend(frase)
        resultado.extend(frases[-1])
        return resultado

    def _fecha_imap(self,fecha):
        MESES = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul",
         "Aug", "Sep", "Oct", "Nov", "Dec"]
        if fecha:
            return f"{fecha.day:02d}-{MESES[fecha.month]}-{fecha.year}"
        else:
            return None
        
    def _frases_fechas(self):
        lista = []
        desde = self._fecha_imap(self.desde)
        hasta = self._fecha_imap(self.hasta)
        if desde is not None:
            lista.append("SINCE")
            lista.append(desde)

        if hasta is not None:
            hasta = self._fecha_imap(self.hasta + timedelta(days=1))
            lista.append("BEFORE")
            lista.append(hasta)

        if lista == [None, None]:
            lista = []

        return lista

    def criterios_imap(self):
        fraces = self._encadenar_con_or()
        fechas = self._frases_fechas()
        lista = fraces+fechas
        if not lista:
            raise ValueError("No hay un dato en especifico")
        return lista