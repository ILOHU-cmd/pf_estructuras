# 2. Dataset y preprocesamiento

## 2.1 Qué es exactamente una transferencia ERC-20

Un contrato ERC-20 emite un evento `Transfer` cada vez que alguien mueve tokens. El evento tiene tres datos: dirección de origen, dirección de destino y cantidad. El dataset exporta ese evento como una fila:

| Columna | Tipo | Significado | Detalle que importa |
|---|---|---|---|
| `token_address` | dirección | Contrato del token | Identifica el token; no hay símbolo ni decimales |
| `from_address` | dirección | Origen | Puede ser la dirección cero en mint o burn |
| `to_address` | dirección | Destino | Puede ser la dirección cero |
| `value` | entero (texto) | Cantidad en unidades mínimas | Hay que dividir por `10**decimales` |
| `transaction_hash` | hash | Transacción que contiene el evento | No se usa en el análisis |
| `log_index` | entero | Posición del evento dentro de la transacción | No se usa |
| `block_number` | entero | Bloque de Ethereum | Se usa para estimar el mes |

> **Idea clave.** `value` no está en dólares ni en tokens: está en la unidad mínima del contrato. USDC usa 6 decimales; DAI usa 18. Si no se normaliza, un valor de `1000000` parece un millón cuando en USDC son 1 USD.

### Direcciones y mayúsculas

Las direcciones Ethereum son hexadecimales y pueden venir con *checksum* (mayúsculas mezcladas). `0xAbC...` y `0xabc...` son la misma dirección. El notebook hace `str.lower()` en todas las columnas de direcciones antes de comparar o agrupar. Si no se hiciera, el mismo exchange aparecería dos veces y se romperían los grados, los componentes y las comunidades.

### La dirección cero

`0x0000000000000000000000000000000000000000` se usa para emitir (mint) y quemar (burn) tokens. No es una billetera real. En T1 y T2 se elimina; en T3 y T4 se hereda el filtro de T2. Si se dejara, aparecería como un nodo gigante artificial conectado con medio dataset.

## 2.2 Dimensiones y periodo

| Métrica | Valor |
|---|---:|
| Transferencias totales | 38.901.039 |
| Tokens distintos | 28 |
| Direcciones únicas (aprox.) | 6.083.422 |
| Transferencias en stablecoins | 4.326.261 |
| Transferencias con un exchange etiquetado | 902.266 |
| Exchanges etiquetados | 296 (247 CEX, 49 DEX) |
| Contrapartes con actividad | 172.596 |
| Rango de bloques | 6.525.201 – 10.000.000 |
| Periodo aproximado | octubre 2018 – mayo 2020 |

El dataset **no trae timestamps**. El mes se estima con un tiempo medio de bloque de 13,5 segundos desde una fecha base (`2018-10-08`, bloque 6.525.201). Es una aproximación: el tiempo real de bloque varía y hubo eventos que lo alteraron. Para el análisis mensual es suficiente; para estudiar shocks de corto plazo, no.

> **Ojo.** La última fila mensual (abril de 2020) tiene solo 149.210 transferencias porque el dataset termina en el bloque 10.000.000, a comienzos de ese mes. No es una caída real del mercado; es un artefacto del corte.

## 2.3 Por qué stablecoins y por qué USDC/DAI

El dataset tiene 28 tokens, pero no todos son comparables en dólares sin precios históricos. USDC y DAI son stablecoins: su precio objetivo es 1 USD, así que se pueden sumar directamente. Eso permite construir un grafo de **liquidez en USD** sin inventar precios.

- **USDC** tiene 6 decimales: `value / 10**6`.
- **DAI** tiene 18 decimales: `value / 10**18`.
- Se excluyen valores no positivos, auto-lazos y la dirección cero.

El preprocesamiento también contempla USDT en la constante `STABLECOINS`, pero en los flujos que sobreviven al filtro de contrapartes principales solo aparecen USDC y DAI. El notebook describe el análisis como USDC/DAI, que es lo que efectivamente se usa.

## 2.4 `preprocess.py` de arriba a abajo

### 2.4.1 Idea general

El CSV original pesa 8,3 GB y tiene 38,9 millones de filas. Cargarlo con pandas requeriría mucha memoria y el notebook de Colab no lo necesita. `preprocess.py` hace **una sola pasada en streaming** con el módulo `csv` de la biblioteca estándar y escribe ocho archivos compactos.

```text
token_transfers_full.csv (8,3 GB)
        │
        ├─ filtro stablecoin ──► flujos agregados (src, dst)
        ├─ filtro exchange ────► contrapartes y volúmenes
        ├─ muestra USDC ───────► usdc_sample.csv
        └─ contadores ─────────► summary.json, monthly, tokens, labels
```

La memoria no crece con el número de filas, sino con el número de **pares distintos** y **direcciones distintas**. Por eso cabe en ~3 GB de RAM y tarda ~4 minutos.

### 2.4.2 Constantes y etiquetas

```python
STABLECOINS = {
    "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48": ("USDC", 6),
    "0xdac17f958d2ee523a2206206994597c13d831ec7": ("USDT", 6),
    "0x6b175474e89094c44da98b954eedeac495271d0f": ("DAI", 18),
}
USDC = "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
TOKEN_RE = re.compile(r"^0x[0-9a-f]{40}$")

def load_exchanges(path):
    out = {}
    with path.open(newline="", encoding="latin-1") as fh:
        for row in csv.DictReader(fh):
            addr = row["address"].strip().lower()
            if TOKEN_RE.match(addr):
                out[addr] = {"type": row["type"].strip(), "name": row["name"].strip()}
    return out
```

- El diccionario asocia cada contrato con su símbolo y sus decimales. Es la tabla de normalización.
- `load_exchanges` lee las etiquetas con `latin-1` porque hay nombres con tildes y el archivo no está en UTF-8.
- `TOKEN_RE` valida que la dirección tenga exactamente 40 caracteres hexadecimales; así se descartan filas basura.
- Se guarda `type` (`cex` o `dex`) y `name` para las visualizaciones.

### 2.4.3 El bucle de streaming

```python
with args.input.open(newline="", encoding="utf-8", errors="replace") as fh:
    reader = csv.reader(fh)
    next(reader)  # cabecera
    for row in reader:
        n_rows += 1
        token = row[0].lower()
        src = row[1].lower()
        dst = row[2].lower()
        block = int(row[6])
        min_block = min(min_block, block)
        max_block = max(max_block, block)
        token_counts[token] += 1
        addr_hashes.add(hash(src))
        addr_hashes.add(hash(dst))
        month = (genesis_like + datetime.timedelta(
            seconds=(block - 6_525_201) * 13.5)).strftime("%Y-%m")
        monthly[month][0] += 1

        if token == USDC and rng.random() < p_usdc:
            usdc_sample.append(row)

        if token not in STABLECOINS:
            continue
        symbol, decimals = STABLECOINS[token]
        value = float(row[3]) / (10**decimals)
        monthly[month][1] += 1
        monthly[month][2] += value

        is_src = src in exchanges
        is_dst = dst in exchanges
        if not (is_src or is_dst):
            continue
        rows_with_exchange += 1
        agg = flows[(src, dst)]
        agg[0] += value
        agg[1] += 1
        agg[2][symbol] += 1
```

Puntos finos:

- `encoding="utf-8", errors="replace"` evita que una fila mal codificada tumbe el proceso.
- `addr_hashes` guarda `hash(src)` y `hash(dst)` en un `set` de enteros de 64 bits. Es una forma barata de estimar direcciones únicas: con 6 millones de entradas, la probabilidad de colisión es despreciable. El conteo es aproximado y depende del `hash` de Python, pero el orden de magnitud es correcto.
- El mes se calcula con `block` y no con una fecha real porque el CSV no trae timestamp.
- El muestreo USDC se hace **antes** del filtro de stablecoins y solo para USDC. Es un muestreo de Bernoulli por fila, no por dirección.
- `flows[(src, dst)]` acumula tres cosas: volumen USD, número de transferencias y un `Counter` de tokens. La clave es el par ordenado: la dirección importa.
- Solo se registran filas donde **al menos un extremo es un exchange etiquetado**. Si ambos son billeteras, la fila se ignora para el grafo de liquidez. Eso hace que el grafo sea exchange-céntrico, no la red completa.

### 2.4.4 La muestra USDC y su matemática

```python
p_usdc = args.usdc_target / 2_278_533  # ~0.1317
if token == USDC and rng.random() < p_usdc:
    usdc_sample.append(row)
```

- `2.278.533` es el número de filas USDC del dataset, conocido de antemano.
- `p = 300.000 / 2.278.533 ≈ 0,1317`. Cada fila USDC se incluye con probabilidad 13,17 %.
- El valor esperado es 300.000; el resultado real fue **300.647** porque es una binomial, no un corte exacto.
- La semilla es 42, así que la muestra es reproducible.
- Es una muestra de **filas**, no de aristas únicas ni de direcciones. Una billetera con muchas transferencias tiene más probabilidad de aparecer; una con una sola transferencia puede quedar fuera. Eso subestima componentes pequeños y hojas, pero conserva la estructura global.

> **Ojo.** No se puede decir “tomé una muestra aleatoria de direcciones”. Es una muestra aleatoria de transferencias USDC. La diferencia importa si el profesor pregunta por sesgo.

### 2.4.5 Selección de las 2.000 contrapartes

```python
def wallet_score(addr):
    return math.log10(1 + wallet_vol[addr]) + 0.5 * math.log10(1 + wallet_cnt[addr])

ranked = sorted(wallet_vol, key=wallet_score, reverse=True)
top_wallets = set(ranked[:args.top_wallets])
keep = set(exchanges) | top_wallets
```

- `wallet_vol` acumula el volumen USD de una billetera cuando interactúa con un exchange.
- `wallet_cnt` cuenta cuántas transferencias hizo con exchanges.
- El puntaje mezcla volumen y actividad: `log10(1+volumen) + 0,5·log10(1+conteo)`. El logaritmo evita que una sola ballena desplace a billeteras que conectan varios exchanges; el 0,5 da más peso al volumen que al conteo, pero no lo deja dominar.
- Se conservan las 2.000 mejores contrapartes **más todos los exchanges etiquetados**. El grafo final tiene 2.075 nodos: 296 exchanges y 2.000 billeteras, menos solapamientos (las billeteras no son exchanges, así que no hay solapamiento; la diferencia es que algunos exchanges no aparecen en ninguna arista).
- ¿Por qué 2.000? Es un compromiso entre tamaño (PageRank, Louvain y Dinic corren en menos de un segundo) y cobertura. No se hizo un barrido formal de sensibilidad; es una limitación que conviene reconocer.

### 2.4.6 Escritura de flujos

```python
for (src, dst), (vol, cnt, toks) in sorted(flows.items()):
    if src not in keep or dst not in keep:
        continue
    row = [src, dst, node_name(src), node_name(dst),
           node_type(src), node_type(dst),
           f"{vol:.6f}", cnt, "|".join(sorted(toks))]
    wf.writerow(row)
    n_flow_rows += 1
    if src in exchanges and dst in exchanges:
        wd.writerow(row)
        n_direct_rows += 1
```

- Se conserva una arista solo si **ambos** extremos están en `keep`. Si una billetera no quedó en el top-2000, su arista desaparece.
- `node_name` devuelve el nombre del exchange o `wallet:0x...` para una billetera.
- `node_type` devuelve `cex`, `dex` o `wallet`.
- `tokens` guarda los símbolos separados por `|`; en la práctica, USDC y DAI.
- El archivo `stablecoin_flows.csv` tiene 6.739 filas; `exchange_direct_flows.csv` tiene 107 (solo exchange → exchange).

### 2.4.7 Proyección por billeteras compartidas

```python
for wallet, exs_set in wallet_exchanges.items():
    exs = sorted(exs_set)
    if len(exs) < 2:
        continue
    if len(exs) > args.max_wallet_exchanges:
        skipped_wallets += 1
        continue
    for i in range(len(exs)):
        for j in range(i + 1, len(exs)):
            a, b = exs[i], exs[j]
            key = (a, b) if a < b else (b, a)
            shared[key]["wallets"] += 1
            shared[key]["volume"] += wallet_vol[wallet]
```

- Para cada billetera que interactuó con **dos o más exchanges**, se conectan todos los pares de exchanges con los que trató.
- El peso es el número de billeteras compartidas entre esos dos exchanges.
- `max_wallet_exchanges=50` evita la explosión combinatoria de una billetera que tocó decenas de exchanges. En este dataset no se omitió ninguna (`n_wallets_skipped_projection = 0`).
- El campo `volume` suma el volumen total de la billetera, no el mínimo entre ambos exchanges; el comentario del código dice “mínimo”, pero la implementación no lo hace. En el notebook **solo se usa `shared_wallets` como peso**, así que el resultado no se ve afectado. Es un detalle que conviene corregir si se reutiliza el archivo.
- Resultado: 1.213 pares, 88 exchanges conectados. Los otros 208 exchanges no comparten ninguna contraparte del top-2000, lo que ya es una señal de fragmentación.

### 2.4.8 Archivos generados

| Archivo | Filas / tamaño | Para qué se usa |
|---|---:|---|
| `summary.json` | 1 objeto | Cifras globales y reproducibilidad |
| `monthly_transfers.csv` | 19 meses | Figuras de actividad |
| `token_counts.csv` | 28 tokens | Top de tokens y mapa de símbolos |
| `exchange_labels.csv` | 296 filas | Nombres y tipos de exchanges |
| `stablecoin_flows.csv` | 6.739 aristas | T2, T3, T4 |
| `exchange_direct_flows.csv` | 107 aristas | Validación exchange–exchange |
| `exchange_shared_wallets.csv` | 1.213 pares | Validación de T3 |
| `usdc_sample.csv` | 300.647 filas | T1 |

## 2.5 Cómo los consume el notebook

La celda 2 define `DATA_DIR` y busca `summary.json` en este orden:

1. La variable de entorno `DATA_DIR`.
2. `/content/drive/MyDrive/proyecto_final/data`.
3. `/content/drive/MyDrive/proyecto_grafos/data`.
4. `/content/data`.
5. `data/` relativo al directorio actual.
6. `../data`.

Si no encuentra `summary.json`, lanza `FileNotFoundError` con un mensaje claro. Después, la celda 4 carga los siete CSV, pasa todas las direcciones a minúsculas y arma el mapa `KNOWN_TOKENS` para las figuras. No se vuelve a leer el CSV original en ningún momento.

> **Idea clave.** El notebook es autocontenido con 32 MB de datos derivados. Esa es la razón por la que se puede ejecutar en Colab en menos de un minuto.

## 2.6 Preguntas típicas de esta sección

**¿Por qué no usar todo el dataset en el notebook?** Porque 8,3 GB no caben cómodamente en Colab y el 99 % de las filas no aporta a las preguntas de grafos. El preprocesamiento conserva la estructura relevante y documenta cómo regenerarla.

**¿No se pierde información al quedarse con 2.000 billeteras?** Sí, se pierden colas largas y componentes pequeños. Se gana viabilidad computacional y se conservan los hubs y la estructura global. Es una limitación explícita, no un error oculto.

**¿Por qué el grafo tiene 2.075 nodos y no 2.296?** Porque 296 exchanges + 2.000 billeteras = 2.296, pero solo aparecen en el archivo las direcciones que tienen al menos una arista con ambos extremos en `keep`. Algunos exchanges no tienen flujos con el top-2000 y quedan aislados; no se agregan como nodos sin aristas.

**¿Por qué se usa `hash()` y no `sha256`?** Porque solo se necesita estimar el cardinal de un conjunto, no una huella criptográfica. `hash()` es mucho más barato y la colisión a 64 bits es negligible para 6 millones de elementos.

**¿Por qué el muestreo USDC no es estratificado?** Porque el objetivo era una muestra simple y reproducible para T1, no una estimación de totales. Un muestreo estratificado por mes o por exchange sería mejor para estudios temporales; se puede proponer como trabajo futuro.

<!-- pagebreak -->
