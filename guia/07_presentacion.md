# 8. Guion de exposición (8:40)

El video debe durar **9 minutos o menos**. Este guion está pensado para 8:40 y deja 20 segundos de margen. No lo leas palabra por palabra: úsalo como columna vertebral. Las frases entre comillas son sugerencias literales; el resto son ideas.

## 8.1 Estructura y tiempos

| Tiempo | Bloque | Qué se muestra | Idea que debe quedar |
|---|---|---|---|
| 0:00–0:25 | Gancho | Título del proyecto | “Una caída de un exchange puede aislar a miles de direcciones” |
| 0:25–1:10 | Dataset | Tabla de cifras / figura mensual | 38,9 M de transferencias, 4 proyecciones |
| 1:10–2:35 | T1 | Grafo USDC + barras de impacto | Fragmentación y puntos críticos |
| 2:35–4:00 | T2 | Tabla PageRank + dispersión | Importancia estructural, no solo volumen |
| 4:00–5:35 | T3 | Grafo de comunidades | 13 comunidades, Q=0,614 |
| 5:35–7:20 | T4 | Red de flujo + corte | 56,85 M y 168 aristas |
| 7:20–8:30 | Conclusiones | Tabla comparativa | Coherencia, validación, límites |
| 8:30–8:40 | Cierre | Portada / “gracias” | Restricción Dijkstra respetada |

## 8.2 Guion detallado

### 0:00–0:25 — Gancho

**Pantalla:** título del proyecto y una imagen de la red o del póster.

> “¿Qué pasaría si el exchange más conectado de Ethereum dejara de operar? No hablamos de precio: hablamos de conectividad. En este proyecto tomamos 38,9 millones de transferencias ERC-20 y construimos cuatro modelos de grafos para medir fragmentación, importancia, comunidades y capacidad de liquidez.”

**Por qué funciona:** empieza con una pregunta concreta, no con “hola, mi nombre es…”. El nombre y el curso pueden ir en los primeros 5 segundos o en un rótulo.

### 0:25–1:10 — Dataset

**Pantalla:** tabla de dimensiones y figura mensual.

> “El dataset cubre de octubre de 2018 a mayo de 2020: 38,9 millones de transferencias, 28 tokens y 6,08 millones de direcciones. No tiene precios ni timestamps, así que para el análisis de liquidez nos quedamos con USDC y DAI, que valen 1 dólar por diseño, y normalizamos con sus decimales. El CSV original pesa 8,3 GB; con un preprocesamiento en streaming generamos 32 MB de datos compactos para que el notebook corra en Colab.”

**Transición:** “Con esos datos construimos cuatro proyecciones. La primera es la red de pagos USDC.”

### 1:10–2:35 — T1

**Pantalla:** definición de punto de articulación, luego barras de impacto.

> “T1 pregunta qué tan fragmentada está la red USDC y quién es crítico. Modelamos un grafo no dirigido y no ponderado: los vértices son direcciones y las aristas son transferencias. Implementamos Union–Find para componentes y Tarjan iterativo para puntos de articulación y puentes. Validamos Tarjan contra fuerza bruta en una bola de 300 nodos.”

> “Resultado: 194.484 vértices, 177.875 aristas y 36.618 componentes. La componente gigante tiene 110.596 vértices, el 56,9 %. Hay 28.587 puntos de articulación y 141.674 puentes. El nodo más crítico es Binance 1: al eliminarlo, 19.447 vértices se separan de la componente principal.”

> “La lectura real: la red tiene un núcleo alrededor de Binance y una periferia enorme de billeteras hoja. La caída de un hub no desconecta todo, pero sí aísla a decenas de miles de direcciones.”

**No digas:** “hay 141.674 puentes, entonces la red es 80 % frágil”. Los puentes son en su mayoría aristas hacia hojas. El dato fuerte es el daño de Binance 1.

### 2:35–4:00 — T2

**Pantalla:** tabla top-5 y dispersión PageRank vs in-strength.

> “T2 pregunta qué exchanges son sistémicamente importantes. Ahora el grafo es dirigido y ponderado por volumen en USD. Implementamos PageRank por iteración de potencias, con manejo de nodos colgantes y damping 0,85. Lo comparamos con PageRank no ponderado y con in-strength.”

> “Binance 1 lidera con 0,090. Pero el caso interesante es 1inch: tiene 0,075 de PageRank con un volumen 18 veces menor que Binance 1. ¿Por qué? Porque muchas contrapartes le envían flujos y él los redistribuye; su posición topológica es la de un agregador. Binance 4, en cambio, sin pesos casi desaparece y con pesos entra al top-5: recibe pocas aristas, pero de enorme volumen.”

> “La correlación de Spearman con in-strength es 0,84 y el solapamiento top-20 es 17 de 20. El volumen explica mucho, pero no todo: la topología aporta el resto.”

**Transición:** “Si los exchanges son importantes, ¿con quién forman ecosistema? Eso es T3.”

### 4:00–5:35 — T3

**Pantalla:** grafo de comunidades y tabla de composición.

> “T3 busca comunidades de liquidez. Usamos un grafo no dirigido ponderado por frecuencia de transferencias, no por volumen, para que unas pocas transferencias gigantes no dominen la partición. Implementamos Louvain desde cero: movimiento local, agregación y 10 reinicios. Lo comparamos con Label Propagation y con las particiones triviales.”

> “Louvain encuentra 13 comunidades con modularidad 0,614. La más grande es el ecosistema Binance: 1.346 nodos, 44 exchanges centralizados y 1.302 billeteras, con el 96 % del peso interno. La segunda es el ecosistema de agregadores DEX: 1inch, ParaSwap y DEX.AG. Después aparecen FTX/Bitmax/Huobi, OasisDEX y otros.”

> “Label Propagation obtiene 0,605 con 24 comunidades: es más barato, pero fragmenta más. La proyección exchange–exchange por billeteras compartidas da solo 0,149: la señal fuerte está a nivel de billetera–exchange, no de exchange–exchange.”

**Transición:** “Ya sabemos quién es importante y con quién se agrupa. Falta saber cuánta liquidez puede moverse y dónde se corta.”

### 5:35–7:20 — T4

**Pantalla:** red de flujo, tabla de corte y barras de sensibilidad.

> “T4 modela la red como una red de capacidades: el volumen observado en USD es la capacidad de cada arista. El origen es Binance 1 y el destino FTX. Implementamos Dinic y Edmonds–Karp para comparar.”

> “El flujo máximo es USD 56,85 millones. Dinic y Edmonds–Karp coinciden exactamente, lo que valida ambas implementaciones. El corte mínimo tiene 168 aristas y su capacidad suma exactamente el flujo. Las mayores son salidas de Binance 1, Poloniex 4, Binance 4, Bitmax 3 y Huobi hacia billeteras que no tienen ruta de vuelta a FTX.”

> “El cuello de botella no es una sola tubería: es una frontera de contrapartes que absorben liquidez. Por eso no basta con aumentar el volumen de una arista; hay que habilitar rutas de retorno.”

> “La sensibilidad muestra que el destino importa: OKEx 1 da 36,24 millones y Huobi 5 da 89,41 millones. Y en tiempo, Dinic es aproximadamente 6 veces más rápido que Edmonds–Karp en esta red.”

**No digas:** “56,85 millones es lo que se transfirió”. Es una cota estructural con capacidades acumuladas de 19 meses.

### 7:20–8:30 — Conclusiones

**Pantalla:** tabla comparativa de las cuatro tareas.

> “Las cuatro tareas comparten dataset y preprocesamiento, pero cada una construye una proyección distinta. T1 muestra fragmentación y fragilidad; T2, importancia estructural; T3, ecosistemas; T4, capacidad y cuellos de botella.”

> “Lo más importante es que todos los algoritmos están implementados desde cero y validados contra una alternativa: DSU contra recorrido, Tarjan contra fuerza bruta, PageRank contra in-strength, Louvain contra Label Propagation, Dinic contra Edmonds–Karp. Y en ninguna parte usamos Dijkstra.”

> “Limitaciones: la muestra USDC puede subestimar componentes pequeños; las etiquetas de exchanges son incompletas; las capacidades son acumuladas, no instantáneas; y Louvain es heurístico. Como trabajo futuro: análisis temporal por mes, precios históricos para más tokens y capacidades instantáneas.”

### 8:30–8:40 — Cierre

> “En resumen: la red Ethereum está fragmentada, Binance 1 es el nodo más sistémico, existen 13 ecosistemas de liquidez y la capacidad Binance–FTX está limitada por una frontera de 168 aristas. Gracias.”

## 8.3 Qué mostrar en pantalla

No muestres el código completo en el video: es ilegible y consume tiempo. Muestra:

1. **Una diapositiva por tarea** con el modelo (qué son V, E, w) y el resultado principal.
2. **Una figura por tarea:** impacto de T1, dispersión de T2, comunidades de T3, corte de T4.
3. **Una tabla final** con las cuatro filas y las columnas “pregunta, modelo, algoritmo, resultado”.
4. **Un recuadro** con “Dijkstra: no usado” y la lista de algoritmos propios.

Si el profesor pide ver código, abre el notebook en la celda del algoritmo y explica solo la función principal; no recorras las 17 celdas.

## 8.4 Si te quedas en blanco

Ten estas cinco frases a mano:

- “El modelo es un grafo `G=(V,E)` donde V son direcciones y E son transferencias.”
- “El algoritmo es propio; lo validamos contra una alternativa.”
- “El resultado principal es … y se interpreta como …”
- “La limitación principal es …”
- “No usamos Dijkstra porque la pregunta no es de caminos mínimos ponderados.”

## 8.5 Versión de 3 minutos (por si acaso)

Si el tiempo se reduce:

1. **0:00–0:20:** dataset y las cuatro preguntas.
2. **0:20–0:50:** T1, 36.618 componentes y Binance 1 separa 19.447.
3. **0:50–1:20:** T2, Binance 1, 1inch y la diferencia entre volumen y topología.
4. **1:20–1:50:** T3, 13 comunidades y Q=0,614.
5. **1:50–2:30:** T4, 56,85 M, 168 aristas y corte = flujo.
6. **2:30–3:00:** validación, limitaciones y “sin Dijkstra”.

## 8.6 Checklist de grabación

- [ ] Notebook ejecutado de principio a fin, sin errores.
- [ ] `data/` disponible en `/content/data` o en Drive.
- [ ] Figuras visibles y con buen tamaño de fuente.
- [ ] Micrófono probado; sin ruido de fondo.
- [ ] Duración ensayada: 8:30–8:50.
- [ ] Rótulo con nombres y curso al inicio.
- [ ] Enlace de YouTube agregado al README y al notebook.
- [ ] Póster PDF a la mano por si se pide.
- [ ] No leer el código línea por línea.
- [ ] Decir “no Dijkstra” al menos una vez, sin sonar defensivo.

<!-- pagebreak -->
