# 7. Validación, complejidad y trampas

## 7.1 Matriz de validación

Una de las cosas que más impresiona en una sustentación no es el resultado, sino demostrar que el resultado está **verificado**. Esta es la matriz que debes tener en la cabeza:

| Tarea | Implementación propia | Validación | Qué se comprobó |
|---|---|---|---|
| T1 | DSU con compresión y unión por tamaño | Recorrido iterativo independiente | Misma partición: 36.618 componentes y mismos tamaños |
| T1 | Tarjan iterativo | Fuerza bruta en bola de 300 nodos | Mismos puntos de articulación (1 vs 1) |
| T2 | PageRank por iteración de potencias | PageRank no ponderado + in-strength | Suma 1; convergencia L1; Spearman y top-20 |
| T3 | Louvain multi-nivel | Label Propagation + particiones triviales | Q 0,614 vs 0,605; triviales 0 y -0,08 |
| T3 | Proyección exchange–exchange | Louvain sobre otra proyección | 6 comunidades, Q 0,149; señal distinta |
| T4 | Dinic | Edmonds–Karp | Mismo flujo exacto; corte = flujo con `assert` |

> **Idea clave.** No se valida contra una librería, se valida contra **otra implementación propia** y contra la definición. Eso es más fuerte para el objetivo del curso: demuestra que entiendes el algoritmo, no que sabes llamar a `networkx`.

## 7.2 Complejidad de cada algoritmo

| Algoritmo | Tiempo | Espacio | Comentario |
|---|---|---|---|
| DSU (con compresión y unión por tamaño) | `O((V+E)·α(V))` | `O(V)` | `α` es casi constante |
| Recorrido de componentes | `O(V+E)` | `O(V)` | Pila explícita |
| Tarjan | `O(V+E)` | `O(V)` | DFS iterativo |
| PageRank (por iteración) | `O(k·(V+E))` | `O(V+E)` | `k` iteraciones hasta converger |
| Modularidad | `O(V+E)` | `O(V)` | Recorre cada arista una vez |
| Louvain (por nivel) | ~`O(E)` | `O(V+E)` | Heurístico; varios niveles |
| Label Propagation | `O(k·E)` | `O(V)` | `k` iteraciones |
| Dinic | `O(V²E)` general | `O(V+E)` | Mejor en redes unitarias |
| Edmonds–Karp | `O(VE²)` | `O(V²)` | Matriz dispersa de capacidades |
| BFS de corte | `O(V+E)` | `O(V)` | Alcanzabilidad en residual |

## 7.3 Argumentos de correctitud (lo que puedes demostrar en el tablero)

### DSU

**Invariante:** `parent[x]` apunta hacia la raíz del conjunto; `size[r]` es el número de nodos del conjunto con raíz `r`; `n_components` es el número de raíces.

- `find(x)` termina porque los punteros forman un bosque sin ciclos.
- La compresión de caminos no cambia la raíz, solo acorta el camino.
- `union(a,b)` cuelga una raíz de otra; el número de conjuntos baja exactamente en 1.
- Por inducción sobre las uniones, al final dos nodos están en el mismo conjunto si y solo si existe un camino entre ellos.

### Tarjan

En un DFS no dirigido, cada arista es de árbol o de retroceso (no hay aristas cruzadas). Para un vértice `u` con hijo `v`:

- `low[v]` es el menor `disc` alcanzable desde el subárbol de `v`.
- Si `low[v] >= disc[u]`, al quitar `u` el subárbol de `v` no puede alcanzar ningún ancestro de `u`; por tanto, `u` es punto de articulación.
- Si `low[v] > disc[u]`, ni siquiera puede alcanzar a `u`; por tanto, `(u,v)` es puente.
- La raíz es la excepción: si tiene un solo hijo, al quitarla el subárbol sigue conectado; solo es AP con dos o más hijos.

### PageRank

La iteración es `PR_{t+1} = (1-d)/N · 1 + d·M·PR_t`, donde `M` es la matriz de transición con la masa de colgantes redistribuida. `M` es estocástica por columnas y, gracias al reinicio uniforme, todos sus elementos son positivos en algún paso; la cadena es irreducible y aperiódica. Por el teorema de convergencia de cadenas de Markov, existe una única distribución estacionaria y la iteración converge a ella. El error L1 decrece geométricamente.

### Louvain

La ganancia de mover un nodo aislado `u` a una comunidad `c` es:

```text
ΔQ = w(u,c)/m - γ · tot_c · k_u/(2m²)
```

Se obtiene expandiendo la definición de modularidad y cancelando los términos que no cambian. El algoritmo solo acepta movimientos con `ΔQ > 0`, así que `Q` no disminuye dentro de un nivel. La agregación conserva `Q` porque las aristas internas se convierten en auto-lazos y las externas en aristas ponderadas. Es una heurística: no garantiza el óptimo global, pero cada nivel mejora o mantiene `Q`.

### Dinic

- El BFS construye un grafo de niveles; cualquier camino `s→t` en él tiene la misma longitud (número de aristas).
- El DFS encuentra un flujo bloqueante: satura todos los caminos del grafo de niveles.
- Después de un flujo bloqueante, el camino más corto en el residual es estrictamente más largo. Como la longitud máxima es `V-1`, hay a lo sumo `V` fases.
- Cada fase cuesta `O(VE)`; el total es `O(V²E)`.
- Cuando no hay camino `s→t` en el residual, el flujo es máximo. El conjunto alcanzable desde `s` define un corte cuya capacidad es igual al flujo (max-flow/min-cut).

## 7.4 Trampas de implementación

| Trampa | Dónde aparece | Cómo se evita |
|---|---|---|
| Direcciones con mayúsculas | T1–T4 | `str.lower()` al cargar |
| Dirección cero | T1, T2 | Filtro explícito `ZERO_ADDRESS` |
| Auto-lazos | T1, T2 | `from != to`, `src != dst` |
| Aristas duplicadas | T1 | `set` de pares canonizados |
| Nodos colgantes | T2 | Reparto uniforme de masa |
| División por cero | T1 densidad, T2 `out_weight`, T3 `m`, T4 capacidades | Guardas `if m == 0`, `if wu > 0` |
| Recursión profunda | Tarjan, DFS de Dinic | Tarjan iterativo; `sys.setrecursionlimit(10_000)` |
| Flotantes | T4 | `eps=1e-9`; `assert` con tolerancia |
| Muestreo sesgado | T1 | Se declara como limitación |
| Etiquetas incompletas | T2–T4 | Se reporta “wallet” y no se inventan nombres |

## 7.5 La restricción de Dijkstra, punto por punto

El enunciado prohíbe Dijkstra. En el notebook:

- No hay función `dijkstra`.
- No se importa `heapq`.
- No se calculan distancias ponderadas entre nodos.
- BFS se usa en tres lugares:
  1. **T1:** recorrido de componentes no ponderadas. El orden no importa; solo se marca visitado.
  2. **T4 Dinic:** niveles por número de aristas, no por peso. Es parte del algoritmo de flujo, no un camino mínimo.
  3. **T4 corte:** alcanzabilidad en el grafo residual, otra vez sin pesos.
- Ninguno de esos BFS usa una cola de prioridad ni relajación de distancias.

> **Si preguntan: “¿Entonces cómo encuentran el camino más corto?”** No lo encontramos, porque no lo necesitamos. Las preguntas son de conectividad, centralidad, comunidades y capacidad. Para flujo máximo, cualquier camino aumentante sirve; Dinic usa niveles por saltos para organizar el trabajo, no para minimizar USD.

## 7.6 Detalles que conviene corregir antes de entregar

Estos son detalles finos que un profesor cuidadoso puede detectar. No hunden el proyecto, pero conviene tener la respuesta preparada o corregirlos.

| Detalle | Dónde | Qué pasa | Cómo responder o corregir |
|---|---|---|---|
| “7,6×” vs 5,9× | Markdown de T4, README, guion y póster | La ejecución guardada da 0,0191 s vs 0,1130 s (5,9×); esos textos citan 7,6× de una corrida anterior | Decir “aproximadamente 6×, depende del entorno”; o actualizar los cuatro textos |
| `bfs_components` usa pila | Celda 9 | Es DFS iterativo, no BFS | “Para componentes es equivalente; el nombre quedó por herencia” |
| Sensibilidad por volumen en T3 | Markdown de T3 | Se menciona pero no se ejecuta | “Quedó como trabajo futuro; la partición principal usa frecuencia” |
| USDT en `preprocess.py` | Constantes | El docstring dice USDC/USDT/DAI; el notebook describe USDC/DAI | “USDT está contemplado, pero en los flujos filtrados solo sobreviven USDC y DAI” |
| RAM del preprocesamiento | Docstring vs README | Dice ~1 GB en un lado y ~3 GB en otro | “Depende del entorno; el orden de magnitud es 2–3 GB” |
| `volume` en proyección | `preprocess.py` | El comentario dice “mínimo”, el código suma el volumen total | “Solo se usa `shared_wallets`; el campo `volume` es descriptivo” |
| Enlace de YouTube | README, notebook | Todavía no está | Agregarlo cuando se suba el video |

> **Idea clave.** Reconocer un detalle fino antes de que lo pregunte el profesor transmite madurez. No intentes ocultarlo; di “eso lo revisamos y aquí está la explicación”.

<!-- pagebreak -->
