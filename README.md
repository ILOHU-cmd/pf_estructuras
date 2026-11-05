# Proyecto final — Teoría de Grafos (UIS)

## La red de transferencias Ethereum: fragmentación, poder y liquidez

**Curso:** Teoría de Grafos — Universidad Industrial de Santander  
**Integrantes:** Emerson Ballesteros Diaz, Jhon Arciniegas y Pablo Alvarez  
**Dataset:** transferencias ERC-20 de Ethereum (`token_transfers_full.csv`) + etiquetas de exchanges y pools stablecoin.

---

## 1. Entregables

| Entregable | Peso | Archivo |
|---|---:|---|
| Notebook importable a Google Colab | 70 % | `proyecto_grafos_ethereum.ipynb` |
| Video explicativo (≤ 9 min) | 15 % | Entrega aparte (no incluido en el repositorio) |
| Poster sintético | 15 % | Entrega aparte (no incluido en el repositorio) |

> **Restricción respetada:** el algoritmo de Dijkstra no se utiliza en ninguna tarea del proyecto. Todas las implementaciones algorítmicas fueron desarrolladas desde cero en el notebook.

---

## 2. Descripción del dataset

El archivo original `ethereum-exchanges/token_transfers_full.csv` ocupa **8,3 GB** y contiene **38.901.039 transferencias** de **28 tokens ERC-20** entre los bloques **6.525.201 y 10.000.000** (octubre de 2018 – mayo de 2020). Participan aproximadamente **6,08 millones de direcciones únicas**.

| Columna | Descripción |
|---|---|
| `token_address` | Contrato del token transferido |
| `from_address` | Dirección de origen |
| `to_address` | Dirección de destino |
| `value` | Cantidad en unidades mínimas del token |
| `transaction_hash` | Hash de la transacción |
| `log_index` | Índice del evento dentro de la transacción |
| `block_number` | Bloque de Ethereum |

Archivos auxiliares:

- `ethereum-exchanges/exchangeLabels.csv`: 296 exchanges etiquetados (247 CEX, 49 DEX).
- `ethereum-exchanges/alphacore_labels_stablecoin.csv`: 181 pools de stablecoins.

Para el análisis de liquidez se usan **USDC** y **DAI**, que se normalizan a USD con sus decimales conocidos (6 y 18). Se excluyen la dirección cero (`0x000…000`, usada para mint/burn), los auto-loops y los valores no positivos.

### Datos compactos generados

La carpeta `data/` ocupa ~32 MB y permite ejecutar el notebook sin el CSV original:

| Archivo | Contenido |
|---|---|
| `stablecoin_flows.csv` | Flujos agregados en USD entre exchanges y sus 2.000 contrapartes principales |
| `exchange_direct_flows.csv` | Solo flujos exchange → exchange |
| `exchange_shared_wallets.csv` | Proyección exchange–exchange por billeteras compartidas |
| `usdc_sample.csv` | Muestra de 300.647 transferencias USDC para la Tarea 1 |
| `monthly_transfers.csv` | Serie mensual de transferencias y volumen stablecoin |
| `token_counts.csv` | Conteo por contrato de token |
| `exchange_labels.csv` | Etiquetas normalizadas de exchanges |
| `summary.json` | Resumen global del dataset |

Para regenerarlos desde el CSV original:

```bash
python preprocess.py \
  --input ethereum-exchanges/token_transfers_full.csv \
  --outdir data
```

El preprocesamiento recorre el CSV una sola vez (streaming), tarda ~4 minutos y requiere ~3 GB de RAM.

---

## 3. Las cuatro tareas

| # | Integrante | Pregunta real | Modelo de grafo | Algoritmo propio | Alternativa comparada |
|---|---|---|---|---|---|
| 1 | Emerson Ballesteros Diaz | ¿Qué tan fragmentada está la red USDC y qué direcciones son críticas? | No dirigido, no ponderado | Union-Find + Tarjan iterativo | BFS/DFS y fuerza bruta |
| 2 | Jhon Arciniegas | ¿Qué exchanges son sistémicamente importantes? | Dirigido, ponderado por USD | PageRank por iteración de potencias | PageRank no ponderado e in-strength |
| 3 | Pablo Alvarez | ¿Qué comunidades de liquidez existen? | No dirigido, ponderado por frecuencia | Louvain multi-nivel con 10 reinicios | Label Propagation y particiones triviales |
| 4 | Todo el grupo | ¿Cuánta liquidez puede rutearse y dónde se corta? | Dirigido con capacidades en USD | Dinic (flujo bloqueante) | Edmonds-Karp |

### Resultados principales

- **T1:** 194.484 vértices, 177.875 aristas, **36.618 componentes**, **28.587 puntos de articulación** y **141.674 puentes**. La componente gigante concentra 110.596 vértices (56,9 %). Al eliminar Binance 1 se separan 19.447 vértices.
- **T2:** PageRank liderado por **Binance 1** (0,0904), **1inch.exchange** (0,0755) y **OasisDEX** (0,0735). 1inch tiene un PageRank alto pese a un volumen mucho menor que Binance 1, lo que evidencia el rol de la topología.
- **T3:** Louvain encuentra **13 comunidades** con **Q ≈ 0,614**; Label Propagation obtiene 24 comunidades con Q ≈ 0,605. La comunidad mayor es el ecosistema Binance (1.346 nodos).
- **T4:** flujo máximo **Binance 1 → FTX ≈ USD 56,85 M**, con un corte mínimo de **168 aristas**. Dinic y Edmonds-Karp coinciden; Dinic es ~7,6× más rápido en esta red.

---

## 4. Cómo ejecutar el notebook

### Google Colab (recomendado)

1. Sube la carpeta `data/` a `/content/data` o a `MyDrive/proyecto_grafos/data`.
2. Abre `proyecto_grafos_ethereum.ipynb` en Colab.
3. Ejecuta todas las celdas (`Runtime → Run all`).
4. Si usas Drive, la celda de configuración busca automáticamente `data/summary.json`; si no, ajusta `DATA_DIR`.

El notebook solo usa `pandas`, `numpy` y `matplotlib` (preinstalados en Colab). No requiere GPU ni instalaciones adicionales.

### Local

```bash
python -m venv .venv
source .venv/bin/activate
pip install pandas numpy matplotlib jupyter
jupyter notebook proyecto_grafos_ethereum.ipynb
```

---

## 5. Estructura del repositorio

```text
proyecto_final/
├── proyecto_grafos_ethereum.ipynb   # entregable principal (70 %)
├── preprocess.py                    # generación de datos compactos
├── data/                            # datos compactos (~32 MB)
├── requirements.txt
├── README.md
└── ethereum-exchanges/              # etiquetas del dataset original
```

---

## 6. Metodología y validez

Cada tarea sigue el mismo esquema:

1. **Problema real** y pregunta de investigación.
2. **Equivalencia** entre el problema y un modelo matemático de grafos.
3. **Algoritmo propio** implementado en el notebook, con explicación de complejidad.
4. **Alternativa algorítmica** comparada empíricamente.
5. **Resultados, interpretación y limitaciones**.

Validaciones incluidas:

- DSU y BFS producen exactamente las mismas componentes.
- Tarjan coincide con fuerza bruta en un subgrafo BFS de 300 nodos.
- Dinic y Edmonds-Karp producen el mismo flujo máximo.
- Louvain se compara con Label Propagation y con las particiones triviales (una comunidad / cada nodo solo).

### Limitaciones

- El dataset está agregado y no contiene timestamps; no se modela el orden temporal.
- El análisis de liquidez se restringe a USDC y DAI; otros tokens no son comparables en USD sin precios históricos.
- Las etiquetas de exchanges son incompletas; muchas billeteras quedan sin identificar.
- La muestra USDC de la Tarea 1 puede omitir componentes pequeños.
- Las capacidades de la Tarea 4 son volúmenes acumulados de 19 meses, no capacidades instantáneas.
- Louvain es heurístico; los 10 reinicios reducen, pero no eliminan, la dependencia del mínimo local.

---

## 7. Entregables externos

- **Video:** se entrega por separado y **no se incluye en este repositorio**.
- **Póster:** se entrega por separado y **no se incluye en este repositorio**.

El notebook, los datos compactos, el preprocesamiento y la documentación son los únicos archivos del repositorio.
