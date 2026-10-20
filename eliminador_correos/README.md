# Eliminador de correos

Busca y elimina mensajes de cuentas IMAP según filtros de remitente, asunto y
fecha. Este proyecto es destructivo: usa `UID STORE` para marcar mensajes y
`EXPUNGE` para eliminarlos definitivamente.

## Uso rápido

```bash
cd eliminador_correos
python prueba.py
python main.py
```

Ejecutá `prueba.py` primero para conocer los nombres de las carpetas que
devuelve el servidor. El programa recorre esas carpetas e ignora la entrada
contenedora `"[Gmail]"`.

## Configuración

El `.env` debe contener:

```env
IMAP_HOST=imap.example.com
IMAP_PUERTO=993
CUENTAS_CSV=cuentas.csv

BORRAR_REMITENTE=promo@example.com;spam@example.com
BORRAR_ASUNTO=Oferta;Publicidad
BORRAR_DESDE=2024-01-01
BORRAR_HASTA=2024-12-31
```

Las listas se separan con `;`. Se debe configurar al menos un filtro. Las
fechas usan `AAAA-MM-DD`; `BORRAR_HASTA` es inclusivo y se traduce al
`BEFORE` del día siguiente.

Los remitentes y asuntos se combinan con `OR`. Las búsquedas IMAP suelen ser
subcadenas, por lo que `SUBJECT "Compra"` también puede coincidir con
`"Compras"`.

El CSV usa:

```csv
correo,clave
usuario@example.com,contraseña
```

No subas `.env` ni `cuentas.csv`.

## Flujo de eliminación

```text
leer configuración
→ construir criterios IMAP
→ conectar cuenta
→ LIST carpetas
→ ignorar "[Gmail]"
→ SELECT readonly=True
→ UID SEARCH
→ SELECT readonly=False
→ UID STORE +FLAGS (\Deleted)
→ EXPUNGE
→ LOGOUT
```

Si `SEARCH` no devuelve UIDs, no se ejecutan `STORE` ni `EXPUNGE`.
Los criterios, UIDs, cantidades, avances y errores se muestran en consola.

## Arquitectura

```text
main.py
  ├── Configuracion
  ├── FiltroBorrado
  ├── ClienteImap
  └── ServicioBorrado
        └── ClienteImap
```

| Módulo | Responsabilidad |
|---|---|
| `main.py` | Ensambla la configuración, el filtro, el cliente y el servicio. |
| `configuracion.py` | Lee y valida `.env` y cuentas. |
| `filtro.py` | Convierte filtros del usuario en argumentos de `SEARCH`. |
| `cliente_imap.py` | Único módulo que ejecuta comandos IMAP. |
| `servicio_borrado.py` | Coordina cuentas, carpetas y etapas de eliminación. |
| `prueba.py` | Descubre las carpetas disponibles en una cuenta. |

El cliente valida los estados de las respuestas IMAP y el servicio cierra cada
sesión en `finally`. La guía completa de arquitectura y desarrollo está en
[`../README.md`](../README.md).

## Validación

Desde esta carpeta:

```bash
python -m py_compile *.py
```

Antes de una ejecución real, probá con una cuenta de prueba y filtros que no
coincidan con nada.

## Riesgos

- `EXPUNGE` es irreversible.
- `EXPUNGE` común puede eliminar otros mensajes que ya estuvieran marcados
  como `\Deleted` en la carpeta.
- Los nombres de carpetas dependen del proveedor.
- No hay confirmación interactiva ni modo simulación.
- La búsqueda por asunto/remitente puede ser parcial.

## Licencia

Pendiente.
