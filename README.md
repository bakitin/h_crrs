# Herramientas IMAP: backup y eliminación

Este repositorio contiene dos herramientas independientes para trabajar con
buzones de correo mediante IMAP:

| Proyecto | Propósito | Efecto sobre el servidor |
|---|---|---|
| [`extractor_correos/`](./extractor_correos/) | Descargar correos a un backup local | Solo lectura |
| [`eliminador_correos/`](./eliminador_correos/) | Buscar y eliminar correos por filtros | Modifica y elimina |

Ambos proyectos usan Python y únicamente la biblioteca estándar. Comparten
algunas ideas y módulos, pero deben considerarse aplicaciones separadas:
el backup conserva mensajes y el eliminador los destruye.

> **Advertencia:** el eliminador ejecuta `EXPUNGE`, que puede borrar mensajes
> de forma irreversible. No lo confundas con el extractor: uno preserva
> información y el otro la elimina.

## Índice

- [Requisitos](#requisitos)
- [Estructura del repositorio](#estructura-del-repositorio)
- [Flujo recomendado](#flujo-recomendado)
- [Extractor de correos](#extractor-de-correos)
- [Eliminador de correos](#eliminador-de-correos)
- [Arquitectura compartida](#arquitectura-compartida)
- [Protocolo IMAP](#protocolo-imap)
- [Guía para desarrolladores](#guía-para-desarrolladores)
- [Seguridad](#seguridad)
- [Limitaciones](#limitaciones)

## Requisitos

- Python 3.10 o superior.
- Acceso IMAP habilitado en cada cuenta.
- Host y puerto IMAP correctos.
- Credenciales válidas.
- Un proveedor que acepte las operaciones que utiliza cada herramienta.

No hay dependencias externas ni archivo `requirements.txt`: se usa la
biblioteca estándar (`imaplib`, `csv`, `email`, `logging`, `pathlib`, entre
otras).

## Estructura del repositorio

```text
extractor_correos/
├── README.md
├── .env.example
├── cuentas.example.csv
├── main.py
├── configuracion.py
├── cliente_imap.py
├── servicio_backup.py
├── analizador.py
└── almacen.py

eliminador_correos/
├── README.md
├── main.py
├── prueba.py
├── configuracion.py
├── cliente_imap.py
├── servicio_borrado.py
└── filtro.py
```

Los archivos `.env` y los CSV con credenciales son locales y no deben
subirse al repositorio.

## Flujo recomendado

### Para conservar mensajes

1. Configurá el extractor.
2. Ejecutá el backup.
3. Revisá que los `.eml` se puedan abrir y que el backup esté completo.
4. Solo después evaluá si necesitás eliminar mensajes.

### Para eliminar mensajes

1. Usá primero el extractor si necesitás conservar una copia.
2. Descubrí los nombres reales de las carpetas con `prueba.py`.
3. Configurá filtros muy específicos.
4. Probá con una cuenta o filtro sin coincidencias.
5. Revisá los criterios y UIDs mostrados en consola.
6. Ejecutá el eliminador únicamente cuando el resultado sea el esperado.

## Extractor de correos

La documentación específica está en
[`extractor_correos/README.md`](./extractor_correos/README.md).

### Propósito

El extractor descarga mensajes de una o varias cuentas y los guarda en disco:

- el mensaje original `.eml`;
- el cuerpo del mensaje;
- los adjuntos, si se habilita esa opción;
- metadatos incluidos en la estructura de carpetas.

Abre las carpetas en modo solo lectura y usa `BODY.PEEK[]`, por lo que no
debería marcar mensajes como leídos.

### Ejecución

```bash
cd extractor_correos
cp .env.example .env
cp cuentas.example.csv cuentas.csv
# editar .env y cuentas.csv
python main.py
```

### Arquitectura

```text
main.py
  ├── Configuracion
  ├── ClienteImap
  └── ServicioBackup
        ├── ClienteImap
        ├── Analizador
        └── Almacen
```

- `Configuracion` lee `.env` y el CSV.
- `ClienteImap` es el único módulo que habla con IMAP.
- `ServicioBackup` coordina cuentas, carpetas y mensajes.
- `Analizador` interpreta los bytes del mensaje.
- `Almacen` crea nombres y escribe el backup local.

## Eliminador de correos

La documentación específica está en
[`eliminador_correos/README.md`](./eliminador_correos/README.md).

### Propósito

El eliminador convierte filtros configurables en una búsqueda IMAP y ejecuta:

```text
SELECT readonly=True
→ UID SEARCH
→ SELECT readonly=False
→ UID STORE +FLAGS (\Deleted)
→ EXPUNGE
```

`EXPUNGE` es definitivo. El proyecto actual recorre las carpetas devueltas
por `LIST` e ignora la entrada contenedora `"[Gmail]"`.

### Ejecución

```bash
cd eliminador_correos
python prueba.py
# revisar las carpetas disponibles
python main.py
```

### Configuración principal

```env
IMAP_HOST=imap.example.com
IMAP_PUERTO=993
CUENTAS_CSV=cuentas.csv
BORRAR_REMITENTE=promo@example.com;spam@example.com
BORRAR_ASUNTO=Oferta;Publicidad
BORRAR_DESDE=2024-01-01
BORRAR_HASTA=2024-12-31
```

Los filtros de remitente y asunto se combinan con `OR`. Las fechas se
convierten a `SINCE` y `BEFORE`; la fecha final se hace inclusiva sumando un
día antes de construir `BEFORE`.

### Arquitectura

```text
main.py
  ├── Configuracion
  ├── FiltroBorrado
  ├── ClienteImap
  └── ServicioBorrado
        └── ClienteImap
```

- `Configuracion` lee y valida los valores.
- `FiltroBorrado` genera la lista de argumentos para `SEARCH`.
- `ClienteImap` ejecuta las conversaciones IMAP y valida sus estados.
- `ServicioBorrado` coordina cuentas, carpetas, marcado y expulsión.
- `prueba.py` ayuda a descubrir los nombres de carpetas del servidor.

## Arquitectura compartida

Los dos proyectos siguen una separación por responsabilidades:

```text
Configuración → transformación de datos → cliente IMAP → servicio → entrada
```

El cliente IMAP no debe decidir qué hacer con cada cuenta: solo ejecuta
operaciones del protocolo. El servicio no debe construir comandos IMAP:
coordina operaciones ya definidas por el cliente. `main.py` arma las
dependencias y arranca el flujo.

Esta separación permite probar el servicio con un cliente falso, sin conectar
a un servidor real.

## Protocolo IMAP

`ClienteImap` utiliza `IMAP4_SSL`.

### Búsqueda

Una lista como:

```python
["FROM", '"promo@example.com"', "SINCE", "01-Jan-2024"]
```

se envía como argumentos separados mediante:

```python
self.imap.uid("SEARCH", None, *criterios)
```

Las respuestas de `imaplib` tienen la forma `(estado, datos)`. Las
operaciones importantes comprueban que `estado` sea `"OK"` y lanzan un error
con la respuesta del servidor si no lo es.

### Eliminación

`UID STORE` solo marca mensajes. `EXPUNGE` es el paso que los elimina.
`EXPUNGE` común puede afectar a otros mensajes de la misma carpeta que ya
estuvieran marcados con `\Deleted` por otro cliente.

## Guía para desarrolladores

### Añadir una función

1. Identificá qué módulo es responsable.
2. Conservá la separación entre configuración, protocolo y orquestación.
3. Validá estados devueltos por IMAP.
4. No ocultes excepciones con `print` ni retornos ambiguos.
5. Evitá comandos destructivos con listas vacías.
6. Agregá una prueba aislada con un cliente falso.
7. Validá sintaxis antes de probar contra una cuenta real:

   ```bash
   python -m py_compile *.py
   ```

### Cliente falso

Un cliente falso puede registrar llamadas para comprobar:

- carpetas seleccionadas;
- argumentos de `SEARCH`;
- orden `SEARCH → STORE → EXPUNGE`;
- que no se llame `STORE` si no hay UIDs;
- que `logout` ocurra en un `finally`.

### Cambios destructivos

Todo cambio que afecte `STORE`, `EXPUNGE`, filtros o selección de carpetas
debe probarse primero sin coincidencias y luego con una cuenta de prueba.

## Seguridad

- No subas `.env`, `cuentas.csv` ni contraseñas.
- Usá contraseñas de aplicación cuando el proveedor lo requiera.
- No dejes credenciales escritas en scripts auxiliares.
- No pegues credenciales en commits, issues, logs ni capturas.
- Ejecutá el eliminador solo después de verificar los criterios y UIDs.
- Conservá un backup antes de una eliminación masiva.

## Limitaciones

- Los nombres de carpetas no son iguales entre proveedores.
- Las búsquedas IMAP suelen ser subcadenas, no coincidencias exactas.
- El eliminador usa `EXPUNGE` común.
- El soporte para tildes y otros caracteres no ASCII depende del servidor.
- El backup y el eliminador son aplicaciones separadas: modificar una no
  actualiza automáticamente la otra.

## Licencia

Pendiente.
