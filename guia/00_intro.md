# Cómo usar esta guía

Esta guía explica **todo el código** del proyecto final, celda por celda, con el nivel de detalle necesario para responder preguntas en la exposición. No es un resumen del notebook: es el “detrás de cámaras” de por qué cada línea existe, qué invariante mantiene y qué error evitaría.

## Tres formas de leerla

- **Si tienes 30 minutos:** lee la sección 1 (proyecto en 60 segundos), la tabla de resultados de la sección 7 y el guion de la sección 8. Con eso puedes presentar.
- **Si tienes 2 horas:** lee las secciones 2 a 6 en orden, mirando el notebook al lado. Detente en los bloques “Si preguntan”.
- **Si quieres dominarlo todo:** lee la guía completa, reproduce el notebook en Colab y resuelve el banco de preguntas de la sección 9 sin mirar las respuestas.

## Convenciones

> **Idea clave.** Una frase que resume lo que debes decir si te piden explicar el bloque en 20 segundos.

> **Ojo.** Un detalle fino, una inconsistencia o una trampa que puede aparecer en la sustentación.

> **Si preguntan.** Una pregunta probable y el inicio de la respuesta correcta.

## Mapa del notebook

El notebook `proyecto_grafos_ethereum.ipynb` tiene 33 celdas: 16 de texto y 17 de código. Todas las celdas de código se ejecutaron sin errores y conservan sus salidas.

| Celdas | Bloque | Qué contiene |
|---|---|---|
| 0–2 | Portada y configuración | Imports, semillas, búsqueda de `data/`, funciones auxiliares |
| 3–6 | Descripción del dataset (10 %) | Columnas, cifras globales, preprocesamiento, tres figuras |
| 7–12 | Tarea 1 | Grafo USDC, DSU, BFS/DFS, Tarjan, ranking de impacto |
| 13–17 | Tarea 2 | Grafo dirigido ponderado, PageRank, ranking y comparaciones |
| 18–23 | Tarea 3 | Grafo no dirigido, modularidad, Louvain, Label Propagation, proyección |
| 24–27 | Tarea 4 | Red de capacidades, Dinic, Edmonds–Karp, corte mínimo, sensibilidad |
| 28–32 | Cierre | Comparación global, conclusiones, reproducibilidad, referencias |

## Archivos del proyecto

| Archivo | Para qué sirve | Qué decir |
|---|---|---|
| `proyecto_grafos_ethereum.ipynb` | Entregable principal (70 %) | “Contiene las cuatro tareas, los algoritmos implementados desde cero y las salidas.” |
| `preprocess.py` | Genera los datos compactos desde el CSV de 8,3 GB | “Recorre el archivo una sola vez en streaming; el notebook no necesita el CSV original.” |
| `data/` | 32 MB de datos derivados | “Resumen, flujos agregados, muestra USDC y etiquetas.” |
| `README.md` | Instrucciones y checklist | “Cómo ejecutar y qué contiene cada entregable.” |
| `poster/poster.pdf` | Póster sintético (15 %) | “Resume problema, modelo, algoritmo y resultado de cada tarea.” |
| `video_guion.md` | Guion del video (15 %) | “Guion cronometrado de 8 a 9 minutos.” |
| `entrega_proyecto.zip` | Paquete de entrega | “Todo excepto el CSV original.” |

> **Ojo.** El proyecto **no es un repositorio git** y no hay commits. Si el profesor pide historial, hay que crearlo antes de la entrega o explicar que se trabajó en carpeta local.

## La restricción que más van a evaluar

El enunciado prohíbe Dijkstra. En el notebook no aparece ninguna implementación de Dijkstra ni se importa `heapq` para caminos mínimos. Las cuatro tareas usan:

- **T1:** Union–Find, recorrido iterativo y Tarjan.
- **T2:** iteración de potencias para PageRank.
- **T3:** Louvain y Label Propagation.
- **T4:** Dinic y Edmonds–Karp.

El BFS aparece en T1 (componentes no ponderadas), en Dinic (grafo de niveles por número de saltos) y en el corte mínimo (alcanzabilidad en el residual). **Ninguno de esos BFS calcula distancias ponderadas**, así que no es Dijkstra disfrazado. Si te preguntan, esa es la respuesta corta.

---

# 1. El proyecto en 60 segundos

## 1.1 El discurso de elevador

> “Tomamos 38,9 millones de transferencias ERC-20 de Ethereum entre 2018 y 2020 y construimos cuatro proyecciones de la misma red: conectividad de la red USDC, importancia de exchanges con PageRank, comunidades de liquidez con Louvain y capacidad máxima con flujo máximo. Cada tarea la resolvimos con un algoritmo implementado desde cero y la validamos contra una alternativa. La red USDC está fragmentada y es frágil; Binance 1 es el nodo más importante, pero 1inch tiene una importancia estructural desproporcionada a su volumen; hay 13 comunidades con modularidad 0,61; y el flujo máximo Binance 1 → FTX es de USD 56,85 millones, limitado por 168 aristas de corte. No usamos Dijkstra en ninguna parte.”

## 1.2 Las cuatro preguntas

| Tarea | Pregunta real | Modelo | Algoritmo propio | Alternativa comparada |
|---|---|---|---|---|
| T1 | ¿Qué tan fragmentada está la red USDC y quiénes son críticos? | No dirigido, no ponderado | DSU + Tarjan iterativo | Recorrido y fuerza bruta |
| T2 | ¿Qué exchanges son sistémicamente importantes? | Dirigido, ponderado por USD | PageRank ponderado | PageRank no ponderado e in-strength |
| T3 | ¿Qué comunidades de liquidez existen? | No dirigido, ponderado por frecuencia | Louvain multi-nivel | Label Propagation y particiones triviales |
| T4 | ¿Cuánta liquidez puede rutearse y dónde se corta? | Dirigido con capacidades USD | Dinic | Edmonds–Karp |

## 1.3 Resultados en una frase por tarea

- **T1:** 194.484 vértices, 177.875 aristas, 36.618 componentes, 28.587 puntos de articulación y 141.674 puentes; al eliminar Binance 1 se separan 19.447 vértices de la componente gigante.
- **T2:** el top-3 es Binance 1 (0,0904), 1inch (0,0755) y OasisDEX (0,0735); 1inch tiene PageRank alto con un volumen 18 veces menor que Binance 1.
- **T3:** Louvain obtiene 13 comunidades con Q ≈ 0,614; Label Propagation obtiene 24 con Q ≈ 0,605; la comunidad mayor es el ecosistema Binance con 1.346 nodos.
- **T4:** flujo máximo Binance 1 → FTX ≈ USD 56,85 M, con 216 aumentos y un corte mínimo de 168 aristas; Dinic y Edmonds–Karp coinciden en el valor.

## 1.4 Por qué el proyecto es coherente

Las cuatro tareas no son cuatro trabajos pegados: comparten el mismo dataset, el mismo preprocesamiento y la misma lógica de “proyección”. Cada tarea elige qué parte de la realidad modelar:

- T1 modela **quién está conectado con quién** (topología).
- T2 modela **cuánto y hacia dónde fluye el valor** (dirección y peso).
- T3 modela **qué tan fuerte se agrupan** esos flujos (mesoescala).
- T4 modela **cuánto puede pasar y dónde se corta** (capacidad).

Ese hilo conductor es lo primero que debes decir en la exposición.

> **Idea clave.** No son cuatro grafos distintos: es el mismo fenómeno visto con cuatro lentes. La coherencia metodológica vale tanto como los resultados.

<!-- pagebreak -->
