# Contexto — Eliminador de correos masivos (IMAP)

> **Documento de traspaso para otro asistente de IA.** Resume qué se construye, cómo trabaja el usuario, qué se decidió, qué está hecho y qué sigue. Redactado por el asistente anterior el 2026-10-20.
>
> **Antes de responder:** leer este documento completo, leer los archivos de `eliminador_correos/` (son pocos) y confirmar al usuario, en 3 o 4 líneas, qué se entendió y desde dónde se retoma.

---

## 0. Resumen

- **Qué se construye:** una herramienta de línea de comandos en Python (solo librería estándar, 3.10+ según el README) que **borra correos en masa** de buzones IMAP según filtros que el usuario escribe en un `.env`: remitentes, asuntos, fecha desde y fecha hasta.
- **Cómo se trabaja:** el usuario está aprendiendo. Quiere recibir guía paso a paso y **escribir el código por su cuenta**. El asistente enseña, revisa y verifica; no resuelve. **La §1 es lo más importante de este documento.**
- **Estado:** Pasos 1 (configuración) y 2 (`filtro.py`) terminados y verificados. **Siguiente: Paso 3, `ClienteImap`** (micro-paso 3.1: `buscar_uids`, solo lectura). La decisión sobre `hasta` está tomada (§3-A).
- **Idioma:** español. El usuario escribe en voseo rioplatense ("guiame", "seguí", "creame"); responder igual (vos).
- **Aviso:** nada de lo relativo al servidor IMAP se probó contra un servidor real en las sesiones anteriores.

---

## 1. Cómo trabajar con el usuario

### Reglas (las pidió explícitamente; frases textuales entre comillas)

1. **Guiar, no resolver.** "No quiero que lo hagas por mí, quiero que me guíes, me gusta programar así." Plan por pasos bien definidos; en cada paso se preparan las cosas nuevas que se van a ver (funciones, módulos, bibliotecas). El código de los archivos del proyecto lo escribe el usuario. Ejemplos genéricos con otros nombres, sí; el código final del proyecto, no.
2. **No asumir nada.** "No quiero que des por sentado nada, no creas que sé cosas que no sé, explicame todo." Todo concepto, función, módulo u operador nuevo se explica desde cero: qué es, para qué sirve, qué devuelve y qué errores da. Incluso hubo que explicar `>>>`, `date`, `raise` y "método privado".
3. **Corto.** "No me des TAAANTO texto... quiero un profesor, pero interesante, no textoooo." Bloques cortos, tablas chicas, 2 a 5 líneas por concepto más un ejemplo mínimo. Sin párrafos largos y sin repetir lo ya dicho.
4. **Problema + herramientas.** "Aparte de darme el problema, dame las herramientas para solucionarlo, no la solución tal cual." Cada observación sigue este molde: **Problema** (1 línea) → **Herramienta** (concepto + ejemplo genérico mínimo) → resuelve el usuario.
5. **Un paso a la vez.** No presentar el paso siguiente hasta que el actual pase todos sus casos.
6. **Dar un orden y un resultado esperado.** Al usuario le sirvió mucho un "Orden sugerido" (ej.: *leer → limpiar y convertir → validar con raise → guardar en self.*; dijo "es una buena forma de guiarme") y una tabla de resultados esperados por caso de prueba.
7. **Pasos chicos.** El 2026-10-20 el Paso 2 se presentó entero (7 herramientas, 1 ejemplo, 8 tareas) y el usuario respondió "no entiendo nada". Aplicar el formato de 5 partes **por micro-paso** (una sola tarea concreta a la vez), partir de un mapa simple (por ejemplo, una tabla "línea del `.env` → frase que entiende el servidor") y preguntar cada tanto qué fue lo que lo perdió. Si dice que no entiende, el paso era demasiado grande: reducirlo, no repetirlo más largo.

### Ciclo de cada vuelta (el que funcionó)

1. Presentar el paso con este formato (lo pidió el usuario el 2026-10-20), siempre en este orden: **Problema → Herramientas** (cada una explicada desde cero, con ejemplo mínimo) **→ Ejemplo genérico de implementación** (en otro dominio, nunca el código del proyecto) **→ Pipeline** (etapas con entrada y salida) **→ Tareas** (lista numerada, cada una con su "listo cuando") más la tabla de resultados esperados.
2. El usuario escribe el código y avisa con **"Ya"**.
3. El asistente **lee los archivos del disco y ejecuta los casos de verdad** (no adivinar ni decir "debería funcionar") y responde con una tabla pasa/falla. Ver §12.
4. Por cada fallo: Problema → Herramienta → ejemplo genérico. Si el problema es un traceback, enseñar a leerlo (de abajo hacia arriba).
5. Repetir hasta que todo pase. Reconocer lo que ya está bien (el usuario lo valora) y recién entonces pasar al paso siguiente.

### Otros acuerdos

- En las sesiones anteriores **no se editó ningún archivo del proyecto del usuario**: solo se leyeron y se probaron con scripts fuera del repo. Mantener eso.
- Las decisiones de la §2 están tomadas. No volver a proponer simulación, confirmación ni registro de lo borrado.
- Informar con fidelidad: si algo falla o no se pudo probar, decirlo.
- Sin commits ni cambios de git salvo que el usuario los pida.

---

## 2. Decisiones ya tomadas (no reabrir)

1. **Los filtros se configuran en el `.env`**, y el usuario elige cuáles usar. Clave vacía o ausente = ese filtro no se aplica. Se pueden combinar.

   ```
   BORRAR_REMITENTE=promo@tienda.com;basura@basura.com
   BORRAR_ASUNTO=Compra;ejemplo;ejemplo2
   BORRAR_DESDE=2023-01-01
   BORRAR_HASTA=2024-01-01
   ```
   Varios remitentes y varios asuntos, separados por `;`. Fechas en formato `AAAA-MM-DD`.
2. **Cómo se combinan (opción B):** dentro de cada lista, **O** (cualquier remitente, cualquier asunto). Entre remitentes y asuntos, **O**. Las fechas acotan siempre, con **Y**. Es decir: `(remitente1 O remitente2 O asunto1 O asunto2) Y fecha_desde Y fecha_hasta`. El usuario vio el ejemplo del riesgo (un "Oferta de trabajo" de su jefe se borraría con un asunto "Oferta") y eligió B.
3. **Sin registro de lo borrado.** "No quiero dejar registro de lo que se elimina, porque ya sé lo que se va a eliminar, sí o sí lo vamos a eliminar." Tampoco simulación (*dry-run*) ni confirmación interactiva. El usuario fue advertido de que borrar es irreversible y mantuvo su decisión.
4. **Única protección acordada:** `Configuracion` se niega a arrancar (`ValueError`) si los cuatro filtros están vacíos, porque una búsqueda sin criterios equivale a `ALL` y vaciaría el buzón. Ya está implementada.
5. **Borrado definitivo** (marcar `\Deleted` + expulsar), sin pasar por la papelera. Lo propuso el asistente y el usuario no lo objetó, pero **no hubo confirmación explícita**: confirmarlo de pasada al llegar al Paso 3.
6. **Paso 0 omitido.** Se había propuesto explorar IMAP a mano en la consola; el usuario dijo "el 0 no hace falta, yo sé que sí funciona todo". Consecuencia: **no se conocen las capacidades de su servidor** (`UIDPLUS`, `MOVE`, nombre de la papelera). Sí tiene un servidor real funcionando: el extractor de backup ya anda contra él.
7. **Proyecto aparte.** El eliminador vive en `eliminador_correos/`, con copias de las piezas del extractor, para no tocar el backup.
8. **Solo `imaplib` (librería estándar).** Se evaluaron `imap_tools` e `IMAPClient` (traducen filtros a criterios) y se recomendó no usarlas: el README promete "solo librería estándar" y el usuario quiere aprender cómo se arma la consulta. Se infiere que el usuario aceptó (respondió "sigamos con la guía"); no lo dijo con esas palabras.

---

## 3. Decisiones pendientes

| | Pregunta | Notas |
|---|---|---|
| **A** | **¿`BORRAR_HASTA` incluye ese día?** | **RESUELTA el 2026-10-20: SÍ, `hasta` incluye su día** (se manda `BEFORE` con `hasta + timedelta(days=1)`; así los dos extremos se comportan igual). Contexto de la pregunta: En IMAP `SINCE 01-Jan-2023` **incluye** el 1 de enero, pero `BEFORE 01-Jan-2024` **excluye** el 1 de enero de 2024. Si `hasta` debe incluir su día, hay que mandar `BEFORE` con la fecha + 1 día (`timedelta(days=1)`). Sugerencia: lo más intuitivo para "hasta 2024-01-01" es incluirlo. Decide el usuario. |
| B | ¿En qué carpetas se busca? | Todas / una lista en el `.env` / excluir papelera y enviados. `ClienteImap.listar_carpetas()` devuelve todas. |
| C | ¿Qué mensajes en pantalla se conservan? | Sin registro de lo borrado, pero el `main.py` heredado configura `logging` a archivo y pantalla. Preguntar si quiere avisos de progreso y errores en pantalla, y si quiere un conteo final (ojo: un conteo no es un registro de qué se borró). |
| D | Punto de entrada | El usuario está adaptando `main.py` dentro de `eliminador_correos/`. Como es un proyecto aparte, no hace falta un `eliminar.py` (se había sugerido para no confundirlo con el backup). Confirmar. |
| E | Tildes y ñ en asuntos/remitentes | Ver §8-6. Se decide al llegar. |
| F | Buzón o carpeta de pruebas | La traducción de filtros a criterios IMAP nunca se probó contra un servidor. Recomendar una primera corrida real sobre una cuenta o carpeta de prueba (una sola vez; no insistir). |

---

## 4. Estructura del repositorio

```
/home/bakitin/Projects/extractor_correos/        ← raíz del repo git
├── .git/   .vscode/
├── extractor_correos/        ← herramienta de BACKUP; terminada según README e historial. No tocar.
│   ├── main.py  configuracion.py  cliente_imap.py  analizador.py  almacen.py  servicio_backup.py
│   └── README.md  .env.example  cuentas.example.csv  .gitignore
└── eliminador_correos/       ← proyecto NUEVO (el que se guía)
    ├── configuracion.py      ← Paso 1 HECHO, escrito por el usuario
    ├── cliente_imap.py       ← copia idéntica del extractor, sin adaptar
    ├── servicio_backup.py    ← copia idéntica; se reemplazará por servicio_borrado.py
    ├── main.py               ← copia a medio adaptar: ROTA (ver §13)
    ├── pruebas.py            ← script de prueba del usuario (imprime configuracion.hasta)
    ├── README.md             ← copia del README del extractor, sin adaptar
    ├── .env  cuentas.csv     ← solo valores de ejemplo; ignorados por git
    ├── .gitignore            ← copia del del extractor
    └── contexto.md           ← este archivo
```

Arquitectura del extractor (y del eliminador, que la sigue): **una clase por responsabilidad**, cada una recibe lo que necesita por el constructor.

| Módulo | Responsabilidad |
|---|---|
| `Configuracion` | Lee `.env` y `cuentas.csv`, valida y entrega valores tipados |
| `ClienteImap` | Único módulo que habla con el servidor IMAP |
| `ServicioBackup` (→ `ServicioBorrado`) | Orquesta cuentas y carpetas; aísla errores con `try/except` |
| `main.py` | Arma los objetos y arranca |

Estilo del usuario: nombres en español, docstring de una línea al inicio de cada archivo, `__init__` que solo guarda datos, comentarios con la explicación del concepto junto a la línea, bloques separados por líneas en blanco o por rótulos (`#-----LEER-----`), `logging` con `basicConfig`. Igualar ese estilo en los ejemplos.

---

## 5. Plan por pasos

| Paso | Qué | Estado |
|---|---|---|
| 0 | Explorar IMAP a mano en la consola (`python -i`) | Omitido por el usuario |
| 1 | Filtros en el `.env`; `Configuracion` los lee, convierte y valida | ✅ Hecho y verificado (§6) |
| 2 | `filtro.py`: convertir la configuración en criterios de búsqueda IMAP | ✅ Hecho y verificado (7 filas + casos extra). Método público `FiltroBorrado.criterios_imap()` |
| 3 | `ClienteImap`: buscar con criterios en modo escritura, marcar `\Deleted`, expulsar por lotes, comprobar `estado` | ⏳ **En curso:** micro-paso 3.1 = `buscar_uids` (solo lectura) |
| 4 | `ServicioBorrado` + punto de entrada | Pendiente |
| 5 | README, `.env.example`, `cuentas.example.csv`, limpieza de claves viejas (`DESTINO`) | Pendiente |
| 6 | Opcional: tildes/ñ, Gmail, mejoras al extractor | Pendiente |

---

## 6. Código actual: `configuracion.py` (Paso 1, verificado)

- `Configuracion(ruta_env)` lee el `.env` con `partition("=")` y expone:
  `host` (str), `puerto` (int), `ruta_cuentas` (Path), `remitentes` (list[str]), `asuntos` (list[str]), `desde` (date | None), `hasta` (date | None).
- `leer_cuentas()` devuelve una lista de dicts con las claves `correo` y `clave` (`csv.DictReader`).
- Claves obligatorias: `IMAP_HOST`, `IMAP_PUERTO`, `CUENTAS_CSV` (`KeyError` si faltan). Las `BORRAR_*` son opcionales: ausente equivale a vacío. `DESTINO` y `EXTRAER_ADJUNTOS` ya no se leen.
- Métodos privados: `_limpiar_listas` (corta por `;`, `strip()`, descarta vacíos), `_configuracion_fechas` (convierte cada fecha por separado; compara solo si hay las dos), `_validar_datos` (al menos un filtro con valor).
- Errores: `ValueError` si una fecha no es ISO válida, si `hasta < desde` ("Las fechas no tienen sentido") o si los cuatro filtros quedan vacíos ("Debe de dar por lo menos un parametro para elminar").
- Se valida **después** de limpiar (así `" ; ;"` cuenta como vacío).

**Casos verificados (11/11 correctos, ejecutados contra el código real):**

| Caso | Resultado esperado y obtenido |
|---|---|
| 1. `BORRAR_ASUNTO=` vacío | OK, `asuntos=[]` |
| 2. `BORRAR_REMITENTE= a@x.com ; b@x.com ;` | OK, 2 remitentes limpios |
| 3. Falta la línea `BORRAR_HASTA` | OK, `hasta=None` y `desde` conservada |
| 4. `BORRAR_DESDE=2023/01/01` | `ValueError` (formato) |
| 5. `desde` posterior a `hasta` | `ValueError` |
| 6. Los cuatro vacíos | `ValueError` |
| 7. Falta la línea `BORRAR_REMITENTE` | OK, `remitentes=[]` |
| Extra: solo `DESDE` / solo `HASTA` | OK, la otra queda en `None` |
| Extra: remitente `" ; ;"` y nada más | `ValueError` |
| Extra: mismo día en `DESDE` y `HASTA` | OK |

---

## 7. Siguiente paso: Paso 2 — `filtro.py`

**Objetivo:** una clase (nombre propuesto: `FiltroBorrado`) que reciba `remitentes, asuntos, desde, hasta` (lo que entrega `Configuracion`) y devuelva la **lista de criterios** de búsqueda IMAP. No usa red: se prueba con `print`.

**Por qué un módulo aparte** (se lo preguntó y se le explicó): `Configuracion` solo lee el `.env`, `ClienteImap` solo habla con el servidor, y alguien debe traducir una cosa a la otra. Se le presentó como una decisión de orden, no una necesidad; también valdría un método en `Configuracion` o en `ClienteImap`. Si el usuario prefiere eso, está bien.

**Resultados esperados** (`hasta` es inclusivo, decisión tomada: ver §3-A):

| Entrada | Salida |
|---|---|
| remitentes `['a@x.com','b@x.com']`, asuntos `['Compra']`, desde 2023-01-01 | `['OR','FROM','"a@x.com"','OR','FROM','"b@x.com"','SUBJECT','"Compra"','SINCE','01-Jan-2023']` |
| solo remitentes `['a@x.com']` | `['FROM','"a@x.com"']` (sin `OR`) |
| remitentes `['a@x.com']`, asuntos `['x']` | `['OR','FROM','"a@x.com"','SUBJECT','"x"']` |
| solo fechas 2023-01-01 y 2024-01-01 | `['SINCE','01-Jan-2023','BEFORE','02-Jan-2024']` (con `hasta` inclusivo, `BEFORE` lleva un día más) |
| desde 2023-03-05 | `SINCE` con `'05-Mar-2023'` (día con cero, mes en inglés) |
| todo vacío | `ValueError` |

**Orden sugerido** (ya entregado al usuario): 1) un criterio por cada remitente y asunto; 2) `OR` delante de cada uno menos el último; 3) `SINCE`/`BEFORE` si hay fechas; 4) validar que no quedó vacía.

**Herramientas ya explicadas al usuario en este paso** (todavía no practicadas):
`OR` en notación prefija que une solo dos cosas (N criterios → N-1 `OR`) · lo que va junto se une con Y · comillas dobles escritas a mano con `f'"{r}"'` · `lista[-1]` y `lista[:-1]` · `append` vs `extend` · `f"{n:02d}"` · lista de meses en inglés indexada con `fecha.month - 1` (y por qué **no** `strftime("%b")`: depende del idioma del sistema) · `raise ValueError` si queda vacía · `timedelta(days=1)` para el `hasta` inclusivo.

**Estado de la presentación:** el Paso 2 se presentó entero en el formato de 5 partes (tareas T0 a T7) y fue demasiado: el usuario respondió "no entiendo nada". Se reinició con una tabla simple (línea del `.env` → frase que entiende el servidor) y **micro-pasos**. Micro-paso 1 (HECHO y verificado con 4 casos; el usuario lo resolvió tras entender que un `return` dentro del `for` corta la función): un método `_frases_remitentes` que convierta `self.remitentes` en una lista de frases como `['FROM', '"a@x.com"']`. Micro-paso 2 (HECHO y verificado con 4 casos): `_frases_asuntos`, igual al anterior pero con `SUBJECT` (después, como mejora, unificar los dos métodos con un parámetro). Micro-paso 3 (HECHO y verificado con 5 casos; tuvo que corregir `self` pasado dos veces, un `for` anidado de más y un `append` que anidaba la lista): `_todas_las_frases`, que une las frases de remitentes y de asuntos en una sola lista con `+`. Micro-paso 4 (HECHO y verificado con 7 casos; el usuario dejó la firma como `_encadenar_con_or(self)`, sin parámetro, y llama internamente a `_todas_las_frases()`; funciona y se aceptó). Lo que se pidió originalmente: `_encadenar_con_or(self, frases)`, que recibe la lista de frases y devuelve una lista plana con `OR` delante de cada frase menos la última (0 frases → `[]`; 1 → sin `OR`). Se presentó con la regla N-1, un ejemplo genérico con `+` prefijo sobre números y tres preguntas para rellenar. Micro-paso 5 (HECHO y verificado con 6 casos; la primera versión leía `self.desde`/`self.hasta` y explotaba con `None`, se rehízo para recibir `fecha`). T0 respondida: `hasta` SÍ incluye su día. Micro-paso 6 (HECHO y verificado con 7 casos): `_frases_fechas(self)`, que arma `SINCE` y `BEFORE` (con `hasta + timedelta(days=1)`) según haya una, dos o ninguna fecha. Tuvo que corregir dos cosas: usaba la fecha antes de preguntar si existía, y agregaba `None` a la lista desde un `else`. `_fecha_imap` devuelve `None` si no hay fecha (diseño aceptado). Micro-paso 7 (HECHO y verificado con 7 filas): `criterios_imap(self)` público, junta todo y lanza `ValueError` si queda vacío. **Paso 2 TERMINADO.** Limpieza opcional que se le señaló: borrar el `if lista == [None, None]` de `_frases_fechas`, corregir la variable `fraces`, y más adelante unificar `_frases_remitentes`/`_frases_asuntos`. El usuario probó `criterios_imap` con su `.env` y preguntó por qué el `OR` cruza FROM y SUBJECT: se le explicó que es la opción B (§2-2), no un error. **Paso 3 en curso:** micro-paso 3.1 = `ClienteImap.buscar_uids(carpeta, criterios)` en solo lectura (no borra nada, y es la primera prueba de los criterios contra el servidor real). Después: marcar `\Deleted` y expulsar (confirmar ahí el borrado definitivo, §2-5). Cuando el usuario avise con "Ya", leer `cliente_imap.py` y ejecutar/pedir la prueba.

---

## 8. Notas técnicas de IMAP

*Fuentes: estándar RFC 3501 y lectura del código de `imaplib`. Verificado en esta máquina (Python 3.15.0): `"EXPUNGE"` y `"MOVE"` están en `imaplib.Commands`, así que `imap.uid("EXPUNGE", ...)` es válido; en 3.10 no se comprobó. Nada se probó contra un servidor real.*

1. **Flujo de borrado:** `select(carpeta)` en modo escritura (hoy `listar_uids` fija `readonly=True`) → `uid("SEARCH", None, *criterios)` → `uid("STORE", "1,2,3", "+FLAGS", r"(\Deleted)")` → `expunge()` o `uid("EXPUNGE", "1,2,3")`.
2. **`EXPUNGE` a secas borra todo lo marcado `\Deleted` en la carpeta**, incluso lo que haya marcado otro cliente (Outlook, webmail). `UID EXPUNGE` borra solo los UIDs indicados, pero **exige la extensión `UIDPLUS`** (se ve en `imap.capabilities`). Si el servidor no la tiene, decidir con el usuario: abortar, revisar antes con `UID SEARCH DELETED`, o aceptarlo.
3. **`FROM` y `SUBJECT` buscan por subcadena y sin distinguir mayúsculas.** `SUBJECT "Compra"` también borra "Compras" o "Recompra"; `FROM "a@x.com"` también coincide con "aa@x.com", y `FROM "tienda.com"` toma todo el dominio. El campo `From` incluye nombre y dirección. **Hay que avisar de esto al usuario**, porque en una herramienta de borrado cambia lo que significa cada línea del `.env`.
4. **Fechas:** `SINCE` es inclusivo y `BEFORE` exclusivo. Comparan la fecha interna de llegada al servidor (INTERNALDATE), ignorando hora y zona horaria, la misma que usa el backup. Existen `SENTSINCE`/`SENTBEFORE` (cabecera `Date`), no usados. Formato `01-Jan-2023`, con el mes en inglés. `imaplib.Months` es `['', 'Jan', ..., 'Dec']` (el índice es el número de mes) y sirve para eso, pero no está en `imaplib.__all__`, o sea que no es API pública declarada.
5. **`imaplib` y los argumentos:** une los argumentos con espacios y **no agrega comillas**: los textos con espacios o `@` se mandan como `'"texto"'`. Los `str` se codifican en ASCII. `uid()` devuelve `(estado, datos)`. Un `BAD` lanza `IMAP4.error`; un `NO` vuelve como valor, así que en operaciones destructivas hay que comprobar `estado != "OK"` y hacer `raise` (el código del proyecto hoy ignora `estado` en todos lados). `respuesta[0].split()` sobre `b''` da `[]`: nada que borrar. Un conjunto de UIDs vacío en `STORE` es un `BAD`: no mandarlo.
6. **Tildes y ñ:** un `str` no ASCII lanza `UnicodeEncodeError`. Opciones, a evaluar con el servidor real: `CHARSET UTF-8` con el texto como *literal* (`imap.literal = texto.encode("utf-8")`; en `imaplib` el literal se agrega **al final** del comando como `{n}`, o sea cabe uno por comando, salvo que `literal` sea una función que el llamador maneje); `imap.enable("UTF8=ACCEPT")` si el servidor lo soporta (RFC 6855); o filtrar esos asuntos en el cliente bajando solo los encabezados con `BODY.PEEK[HEADER.FIELDS (FROM SUBJECT)]`. Es el Paso 6; no adelantarlo.
7. **Lotes:** muchos UIDs en un solo comando lo vuelven demasiado largo. Partir la lista (por ejemplo de a 500) y unir cada lote con `",".join(uids)`.
8. **Gmail:** si algún día se usa contra Gmail, borrar de INBOX solo quita la etiqueta; el correo sigue en "Todos". Aquí no aplica (el README menciona OVH), pero avisar si cambia el host.
9. **Carpetas:** `listar_carpetas()` devuelve los nombres tal cual los manda el servidor, con comillas si hay espacios (`'"Elementos enviados"'`), y se pasan igual a `select`. Los UIDs son `str` en todo el proyecto. Algunas entradas de `LIST` pueden no ser seleccionables (`\Noselect`): `select` falla y hay que aislar el error por carpeta.

---

## 9. Herramientas ya pensadas para los pasos 3 a 5

**Paso 3 — `ClienteImap`:** parámetros con valor por defecto (`def f(a, b=None, c=True)`) · `f(*lista)` equivale a `f(*elementos)` y sirve para `uid("SEARCH", None, *criterios)` · `",".join(uids)` · lotes con `for i in range(0, len(x), n): x[i:i+n]` · *raw strings* `r"(\Deleted)"` (en un `str` normal `"\D"` es una secuencia de escape inválida y avisa) · comprobar `estado` y `raise` · no mandar `STORE`/`EXPUNGE` con lista vacía · `select(carpeta)` sin `readonly`, y si falla, no seguir con esa carpeta. Como `eliminador_correos/cliente_imap.py` es una copia, adaptarlo no rompe el backup.

**Paso 4 — `ServicioBorrado` y entrada:** `try/finally` para que el `logout` ocurra siempre (el `ServicioBackup` actual no lo hace: buen ejemplo para mostrar) · `try/except` por cuenta y por carpeta (ya conoce el patrón) · `logging` (ya lo conoce) · decidir carpetas y mensajes (§3-B y C).

**Paso 5:** README del eliminador, `.env.example` y `cuentas.example.csv` (hoy no existen en `eliminador_correos/` y el `.gitignore` ignora `.env` y `cuentas*.csv`), y limpieza de claves que ya no se leen.

---

## 10. Qué ya se le explicó (repasar en una línea si reaparece)

`>>>` y la consola interactiva (`python`) · `type()` · leer un traceback de abajo hacia arriba · `AttributeError`, `TypeError`, `ValueError`, `KeyError`, `NoneType` · `str.split`, `strip()` devuelve un texto nuevo (los `str` son inmutables), `partition` · valores falsos (`""`, `[]`, `None`, `0`) · `dict.get(clave, defecto)` · comprensión de listas (mostrada, no usada) · `datetime.date`, `date(a, m, d)`, `.year/.month/.day`, `date.fromisoformat`, comparar fechas · expresión condicional `x if c else y` · `raise` · métodos privados con `_` · `and`/`or`/`not` frente a `&` · cortocircuito de `and` · función con y sin paréntesis · `None` frente a `pass` frente a `"Pass"` · devolver varios valores y desempaquetarlos (`a, b = f()`) · `append` frente a `extend` · índices negativos y *slicing* · `f"{n:02d}"` · `timedelta` · `OR` prefijo de IMAP, `SINCE`/`BEFORE`.

---

## 11. Errores típicos que ya aparecieron (para calibrar la guía)

El usuario corrige rápido lo que se le señala, en una o dos vueltas. Errores vistos:

- `&` en lugar de `and` (y `not a & b` sin paréntesis).
- Llamar a un método sin paréntesis (`if self._validar_datos:`), que siempre es verdadero.
- `.get(clave)` sin valor por defecto (apareció cuatro veces).
- Confundir `None`, `pass` y el texto `"Pass"`.
- Recorrer un `str` creyendo que es una lista; `append` de una lista dentro de otra (`[['p']]`).
- Condiciones invertidas (`>` en lugar de `<`) y validaciones demasiado estrictas (exigir los cuatro filtros).
- Ramas del código que no devuelven nada (`return None` implícito) o que dejan atributos sin crear.
- Cambiar el nombre de un método y no actualizar las llamadas.

---

## 12. Cómo verificar su trabajo

Escribir los scripts de prueba **fuera del repo** (carpeta temporal) y ejecutarlos con `PYTHONPATH=<carpeta del proyecto>`: sin eso, Python no encuentra `configuracion.py`. Ejemplo para `Configuracion` (arma un `.env` distinto por caso y no toca el real):

```python
import sys
from pathlib import Path
from configuracion import Configuracion

base = "IMAP_HOST=x\nIMAP_PUERTO=993\nCUENTAS_CSV=cuentas.csv\n"
casos = {
 "1 asunto vacio":  "BORRAR_REMITENTE=a@x.com\nBORRAR_ASUNTO=\nBORRAR_DESDE=2023-01-01\nBORRAR_HASTA=2024-01-01\n",
 "2 espacios y ;":  "BORRAR_REMITENTE= a@x.com ; b@x.com ;\nBORRAR_ASUNTO=Compra\nBORRAR_DESDE=2023-01-01\nBORRAR_HASTA=2024-01-01\n",
 "3 sin HASTA":     "BORRAR_REMITENTE=a@x.com\nBORRAR_ASUNTO=Compra\nBORRAR_DESDE=2023-01-01\n",
 "4 fecha barras":  "BORRAR_REMITENTE=a@x.com\nBORRAR_DESDE=2023/01/01\n",
 "5 desde>hasta":   "BORRAR_REMITENTE=a@x.com\nBORRAR_DESDE=2025-01-01\nBORRAR_HASTA=2024-01-01\n",
 "6 todo vacio":    "BORRAR_REMITENTE=\nBORRAR_ASUNTO=\nBORRAR_DESDE=\nBORRAR_HASTA=\n",
 "7 sin REMITENTE": "BORRAR_ASUNTO=Compra\nBORRAR_DESDE=2023-01-01\nBORRAR_HASTA=2024-01-01\n",
}
ruta = Path(sys.argv[1]) / "prueba.env"      # sys.argv[1] = carpeta temporal
for nombre, extra in casos.items():
    ruta.write_text(base + extra, encoding="utf-8")
    try:
        c = Configuracion(ruta)
        print(nombre, "-> OK", c.remitentes, c.asuntos, c.desde, c.hasta)
    except Exception as e:
        print(nombre, "->", type(e).__name__, e)
```

Importante: imprimir **todos** los valores (no solo "OK"). Una vez pasó un caso "correcto" que en realidad había perdido una fecha en silencio (`desde=None`) y solo se vio por mirar el valor.

Para el Paso 2, el mismo método: crear `FiltroBorrado` con los datos de la tabla de la §7 e imprimir la lista que devuelve.

---

## 13. Pendientes menores y riesgos

- **`eliminador_correos/main.py` está roto** (a medio adaptar): usa `configuracion.destino`, que `Configuracion` ya no define (`AttributeError`), y llama a `ServicioBackup(cliente)` cuando su constructor pide cuatro argumentos. Se arregla solo al llegar al Paso 4; no hace falta tocarlo antes.
- `Configuracion._configuracion_fechas` tiene dos `return` casi iguales seguidos (el de adentro del `if` sobra). Se le ofreció limpiarlo como práctica opcional; no lo aplicó.
- El mensaje de error de "cuatro filtros vacíos" tiene una errata ("elminar").
- Un remitente o asunto que contenga `;` no se puede expresar (es el separador).
- El `.env` se lee desde el directorio actual (`Configuracion(".env")`): ejecutar desde `eliminador_correos/`.
- Falta `.env.example` y `cuentas.example.csv` en `eliminador_correos/` (ver §9).
- `cliente_imap.py` quedó duplicado en las dos carpetas: tiene un costo de mantenimiento; no urgente.
- **Git:** la reorganización en subcarpetas no está registrada. `git status` muestra los archivos de la raíz como borrados (`D`) y las carpetas `extractor_correos/` y `eliminador_correos/` sin seguimiento (`??`). Un `git add -A` los reconoce como renombrados. No hay commits del eliminador.
- Mejoras posibles al extractor (solo si el usuario las quiere): `desconectar()` en un `finally` y comprobar `estado` en las respuestas IMAP.
- El `.env` y `cuentas.csv` actuales contienen solo datos de ejemplo (`imap.ejemplo.co`, `usuario1@midominio.com`). Cuando entren credenciales reales, el `.gitignore` ya los cubre.
