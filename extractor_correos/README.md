# Extractor de correos

Backup local de buzones IMAP. Este proyecto descarga mensajes y adjuntos sin
modificar el servidor.

## Uso rápido

```bash
cd extractor_correos
cp .env.example .env
cp cuentas.example.csv cuentas.csv
# editar .env y cuentas.csv
python main.py
```

Requisitos: Python 3.10+ y acceso IMAP habilitado.

## Configuración

`.env` debe contener:

```env
IMAP_HOST=imap.example.com
IMAP_PUERTO=993
DESTINO=backup
CUENTAS_CSV=cuentas.csv
EXTRAER_ADJUNTOS=si
```

El CSV usa las columnas:

```csv
correo,clave
usuario@example.com,contraseña
```

No subas `.env` ni `cuentas.csv`: contienen credenciales.

## Qué genera

Por cada cuenta, carpeta y mensaje se guarda:

- `<uid>.eml`: mensaje original;
- `cuerpo.txt`: cuerpo en texto plano o HTML;
- `Adjuntos/`: archivos adjuntos, si `EXTRAER_ADJUNTOS=si`.

El backup es reanudable: los mensajes ya guardados se saltan. Los errores se
registran y no detienen necesariamente el resto del proceso.

## Arquitectura

```text
main.py
  ├── Configuracion
  ├── ClienteImap
  └── ServicioBackup
        ├── Analizador
        └── Almacen
```

| Módulo | Responsabilidad |
|---|---|
| `main.py` | Ensambla objetos y arranca el backup. |
| `configuracion.py` | Lee `.env` y el CSV. |
| `cliente_imap.py` | Único módulo que habla con IMAP. |
| `servicio_backup.py` | Coordina cuentas, carpetas y mensajes. |
| `analizador.py` | Extrae asunto, cuerpo y adjuntos del `.eml`. |
| `almacen.py` | Crea carpetas, nombres y archivos locales. |

`ClienteImap` abre las carpetas en solo lectura y usa `BODY.PEEK[]`. La
arquitectura completa del repositorio y las reglas para desarrolladores están
en [`../README.md`](../README.md).

## Validación

Desde esta carpeta:

```bash
python -m py_compile *.py
```

## Advertencia

Este proyecto conserva mensajes; no lo confundas con
[`../eliminador_correos/`](../eliminador_correos/), que ejecuta `EXPUNGE` y
elimina mensajes.

## Licencia

Pendiente.
