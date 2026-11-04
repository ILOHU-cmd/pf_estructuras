# 10. Apéndices

## 10.1 Glosario

| Término | Definición breve |
|---|---|
| **Arista** | Par de vértices que representa una relación; aquí, una transferencia agregada |
| **Auto-lazo** | Arista de un vértice a sí mismo; se elimina |
| **Bridge (puente)** | Arista cuya eliminación aumenta el número de componentes |
| **CEX / DEX** | Exchange centralizado / descentralizado |
| **Componente conexa** | Conjunto maximal de vértices conectados por caminos |
| **Cut vertex** | Vértice cuya eliminación aumenta el número de componentes |
| **Dangling node** | Nodo sin aristas salientes; en PageRank se reparte su masa |
| **DSU / Union–Find** | Estructura para mantener conjuntos disjuntos con `find` y `union` |
| **Flujo máximo** | Máxima cantidad que puede enviarse de `s` a `t` respetando capacidades |
| **Corte mínimo** | Partición de vértices que separa `s` de `t` con capacidad mínima |
| **Grado** | Número de aristas incidentes; en dirigido, in-degree + out-degree |
| **In-strength** | Suma de pesos de las aristas entrantes |
| **Modularidad (Q)** | Medida de calidad de una partición en comunidades |
| **PageRank** | Probabilidad estacionaria de un paseo aleatorio con reinicio |
| **Peso** | Valor numérico de una arista; aquí USD o número de transferencias |
| **Residual** | Grafo con la capacidad que queda tras enviar flujo |
| **Spearman** | Correlación entre rangos |
| **Stablecoin** | Token diseñado para valer 1 USD; USDC y DAI |
| **Top-2000** | Contrapartes principales conservadas en el grafo de flujos |
| **Vértice** | Dirección o entidad del grafo |

## 10.2 Índice de funciones y celdas

| Celda | Símbolo | Qué hace |
|---:|---|---|
| 2 | `DATA_DIR` | Busca la carpeta de datos en Colab o local |
| 2 | `short_addr` | Abrevia direcciones para tablas |
| 2 | `fmt_usd`, `fmt_int` | Formatea cifras |
| 9 | `DSU` | Union–Find con compresión y unión por tamaño |
| 9 | `bfs_components` | Recorrido iterativo para componentes (en realidad DFS) |
| 10 | `tarjan_articulation` | Puntos de articulación y puentes en `O(V+E)` |
| 10 | `count_components` | Cuenta componentes, opcionalmente sin un vértice |
| 10 | `naive_articulation` | Fuerza bruta para validar Tarjan |
| 11 | `node_name_type` | Nombre y tipo de una dirección |
| 11 | `largest_component_without` | Componente mayor al eliminar un nodo |
| 15 | `pagerank` | Iteración de potencias con colgantes |
| 16 | `spearman` | Correlación de rangos sin scipy |
| 20 | `modularity` | Calcula `Q` de una partición |
| 20 | `louvain_once` | Una corrida de Louvain multi-nivel |
| 20 | `louvain` | 10 reinicios y mejor `Q` |
| 20 | `label_propagation` | Etiquetas por vecindad ponderada |
| 25 | `Dinic` | Flujo máximo con niveles y flujo bloqueante |
| 25 | `edmonds_karp` | Flujo máximo con BFS y matriz residual |
| 26 | `run_dinic` | Ejecuta Dinic y mide tiempo |

## 10.3 Comandos y reproducción

### Regenerar los datos

```bash
python preprocess.py \
  --input ethereum-exchanges/token_transfers_full.csv \
  --outdir data
```

Opciones útiles:

```bash
python preprocess.py --help
python preprocess.py --input ... --outdir data --top-wallets 2000 --seed 42
```

### Ejecutar el notebook en local

```bash
pip install -r requirements.txt
jupyter notebook proyecto_grafos_ethereum.ipynb
```

### Ejecutar en Colab

1. Subir la carpeta `data/` a `/content/data` o a `MyDrive/proyecto_grafos/data`.
2. Abrir `proyecto_grafos_ethereum.ipynb`.
3. `Runtime → Run all`.
4. Si la ruta no se encuentra, definir `DATA_DIR` en la celda 2.

### Verificar la restricción

```bash
grep -RniE "dijkstra|heapq" proyecto_grafos_ethereum.ipynb preprocess.py
```

No debe haber coincidencias de implementación. Si aparece la palabra “Dijkstra” en un texto que dice que no se usó, no cuenta como implementación.

## 10.4 Checklist de entrega

- [ ] Verificar que los nombres de los integrantes estén en portada, README y póster.
- [ ] Agregar el enlace de YouTube en README y notebook.
- [ ] Verificar que el notebook corre de principio a fin sin errores.
- [ ] Confirmar que `data/` está incluido y que el notebook lo encuentra.
- [ ] Revisar que no haya Dijkstra ni `heapq` para caminos mínimos.
- [ ] Revisar el detalle 7,6× vs 5,9× en T4.
- [ ] Exportar el póster a PDF y revisar legibilidad a tamaño A1.
- [ ] Probar el video con cronómetro: ≤ 9 minutos.
- [ ] Incluir `README.md`, `requirements.txt` y `data/README.md` en el zip.
- [ ] Confirmar que el zip no incluye el CSV de 8,3 GB.
- [ ] Tener una copia del notebook ejecutado y del PDF por si falla Colab.

## 10.5 Referencias principales

- Tarjan, R. E. (1972). *Depth-first search and linear graph algorithms*. SIAM Journal on Computing, 1(2), 146–160.
- Page, L., Brin, S., Motwani, R., & Winograd, T. (1999). *The PageRank citation ranking: Bringing order to the web*. Stanford InfoLab.
- Blondel, V. D., Guillaume, J.-L., Lambiotte, R., & Lefebvre, E. (2008). *Fast unfolding of communities in large networks*. Journal of Statistical Mechanics: Theory and Experiment, 2008(10), P10008.
- Dinic, E. A. (1970). *Algorithm for solution of a problem of maximum flow in networks with power estimation*. Soviet Mathematics Doklady, 11, 1277–1280.
- Edmonds, J., & Karp, R. M. (1972). *Theoretical improvements in algorithmic efficiency for network flow problems*. Journal of the ACM, 19(2), 248–264.
- Raghavan, U. N., Albert, R., & Kumara, S. (2007). *Near linear time algorithm to detect community structures in large-scale networks*. Physical Review E, 76(3), 036106.
- Ethereum Foundation. *ERC-20 Token Standard*. https://eips.ethereum.org/EIPS/eip-20

## 10.6 Nota final

Si llegaste hasta aquí, ya tienes más material del que necesitas para una exposición de 9 minutos. No memorices las 58 respuestas: memoriza **cinco ideas**:

1. Cada tarea es una proyección distinta del mismo dataset.
2. Todos los algoritmos son propios y están validados contra una alternativa.
3. T1 mide fragilidad; T2, importancia; T3, ecosistemas; T4, capacidad.
4. Los resultados principales son 36.618 componentes, 0,0904 de PageRank para Binance 1, 13 comunidades con Q=0,614 y USD 56,85 M de flujo máximo.
5. No se usó Dijkstra porque ninguna pregunta es de caminos mínimos ponderados.

Con eso, y con la capacidad de explicar el “por qué” de cada línea, el proyecto se defiende solo.
