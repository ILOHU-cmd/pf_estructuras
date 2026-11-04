# Guion del video — máximo 9 minutos

**Título:** *La red de transferencias Ethereum: fragmentación, poder y liquidez*  
**Duración objetivo:** 8:45  
**Formato sugerido:** grabación de pantalla del notebook + voz en off.  
**Consejo:** no leer el notebook; mostrar solo las celdas y figuras clave. Cada integrante presenta su tarea.

---

## 0:00–0:35 — Apertura (Emerson Ballesteros Diaz)

**Pantalla:** portada del notebook.

**Narración:**
> “Hola, somos el grupo de Teoría de Grafos de la UIS. En este proyecto analizamos la red de transferencias de tokens ERC-20 en Ethereum: 38,9 millones de transferencias, 28 tokens y más de seis millones de direcciones entre 2018 y 2020. Nuestro objetivo es responder cuatro preguntas reales usando grafos: ¿qué tan fragmentada está la red?, ¿quiénes son los actores más importantes?, ¿qué comunidades de liquidez existen? y ¿cuánta liquidez puede rutearse entre exchanges?
>
> Una restricción importante: no usamos Dijkstra. Implementamos nuestros propios algoritmos: Union-Find, Tarjan, PageRank, Louvain y Dinic.”

**En pantalla:** resaltar el badge “sin Dijkstra” y la tabla de las cuatro tareas.

---

## 0:35–1:40 — Dataset y preprocesamiento (Emerson Ballesteros Diaz)

**Pantalla:** celda de descripción y figura mensual.

**Narración:**
> “El dataset contiene eventos `Transfer` de tokens ERC-20: token, origen, destino, valor, transacción y bloque. El archivo original pesa 8,3 GB. Para que el notebook sea reproducible en Colab, hicimos un preprocesamiento en streaming que genera solo 32 MB de datos compactos: flujos agregados en stablecoins, una muestra de USDC, etiquetas de exchanges y estadísticas mensuales.
>
> Usamos USDC y DAI porque su valor es comparable 1:1 con el dólar; así podemos sumar volumen entre tokens. Excluimos la dirección cero, que representa mint y burn, y los auto-loops. La figura muestra la actividad mensual: el volumen stablecoin se acelera desde finales de 2019 y alcanza su máximo en febrero de 2020, con casi 9.500 millones de dólares.”

**En pantalla:** tabla de resumen: 38.901.039 transferencias, 28 tokens, 6,08 M direcciones, 296 exchanges.

---

## 1:40–3:30 — Tarea 1: fragmentación y puntos críticos (Emerson Ballesteros Diaz)

**Pantalla:** celda de construcción del grafo USDC, salida de DSU/BFS y tabla de puntos de articulación.

**Narración:**
> “La primera pregunta es qué tan fragmentada está la red de pagos USDC. Modelamos un grafo no dirigido donde cada vértice es una dirección y cada arista indica que hubo al menos una transferencia. No usamos pesos: nos interesa la conectividad.
>
> Implementamos Union-Find con compresión de caminos y unión por tamaño, y lo comparamos con BFS. Ambos encuentran exactamente las mismas 36.618 componentes. La mayor tiene 110.596 vértices, el 56,9 % de la red; el resto son islotes. Es una red global, pero muy fragmentada.
>
> Para encontrar puntos críticos implementamos Tarjan iterativo, que calcula puntos de articulación y puentes en tiempo lineal. Encontramos 28.587 puntos de articulación y 141.674 puentes. Validamos Tarjan contra fuerza bruta en un subgrafo de 300 nodos y coinciden exactamente.
>
> La tabla muestra el impacto: al eliminar Binance 1 se separan 19.447 vértices de la componente gigante. Es decir, los exchanges no solo concentran volumen: son cuellos de botella estructurales. Si una billetera de exchange falla o se bloquea, miles de contrapartes quedan aisladas.”

**En pantalla:** figura de barras de impacto y distribución log-log de componentes.

---

## 3:30–5:15 — Tarea 2: importancia sistémica con PageRank (Jhon Arciniegas)

**Pantalla:** celda del grafo dirigido, tabla de ranking y scatter PageRank vs in-strength.

**Narración:**
> “La segunda pregunta es quiénes son los exchanges más importantes. Aquí el grafo es dirigido y ponderado: los vértices son exchanges más las 2.000 contrapartes principales, y el peso de una arista es el volumen en dólares.
>
> Implementamos PageRank por iteración de potencias, con damping 0,85, manejo de nodos colgantes y criterio de convergencia de 10 a la menos 12. Converge en 137 iteraciones.
>
> El ranking está encabezado por Binance 1, con 0,090; le siguen 1inch.exchange, con 0,0755, y OasisDEX, con 0,0735. El caso de 1inch es interesante: su volumen recibido es mucho menor que el de Binance 1, pero su PageRank es el segundo más alto porque recibe flujos de muchas contrapartes y los redistribuye. Es un agregador.
>
> Comparamos con dos líneas base: PageRank no ponderado y volumen recibido, o in-strength. La correlación de Spearman con in-strength es 0,839, alta pero no perfecta: el volumen explica mucho, pero la posición topológica cambia el orden. Por eso decimos que la importancia sistémica no es solo volumen.”

**En pantalla:** tabla top 5 y figura de dispersión.

---

## 5:15–6:45 — Tarea 3: comunidades con Louvain (Pablo Alvarez)

**Pantalla:** celda de Louvain, tabla de comunidades y grafo agregado de comunidades.

**Narración:**
> “La tercera pregunta es qué comunidades de liquidez existen. Modelamos un grafo no dirigido donde el peso es la frecuencia de transferencias, no el volumen. ¿Por qué? Porque unas pocas transferencias gigantes pueden dominar la partición y ocultar la estructura.
>
> Implementamos Louvain desde cero: fase de movimiento local que maximiza la ganancia de modularidad, fase de agregación y repetición. Usamos 10 reinicios aleatorios y nos quedamos con la mejor partición.
>
> Louvain encuentra 13 comunidades con modularidad 0,614. La comunidad más grande es el ecosistema Binance, con 1.346 nodos; otras giran alrededor de 1inch, FTX, OasisDEX, Bitfinex/KuCoin y HitBTC. Comparamos con Label Propagation: obtiene 24 comunidades y Q igual a 0,605. Louvain logra una partición más compacta y con mayor modularidad.
>
> También proyectamos exchanges que comparten billeteras: solo 88 de los 296 exchanges comparten contrapartes principales, y esa proyección se divide en 6 comunidades. Es otra señal de fragmentación.”

**En pantalla:** grafo de comunidades y barra de modularidad.

---

## 6:45–8:25 — Tarea 4: flujo máximo y cuellos de botella (Todo el grupo)

**Pantalla:** celda de Dinic, tabla del corte mínimo y figura de sensibilidad.

**Narración:**
> “La cuarta pregunta es cuánta liquidez puede rutearse entre dos exchanges y dónde está el cuello de botella. Modelamos una red dirigida con capacidades: cada arista tiene como capacidad el volumen USD agregado. El origen es Binance 1 y el destino es FTX.
>
> Implementamos Dinic: construimos el grafo de niveles con BFS y enviamos flujo bloqueante con DFS. Como alternativa implementamos Edmonds-Karp. Ambos obtienen el mismo flujo máximo: 56,85 millones de dólares, con 216 aumentos. Dinic tarda 0,015 segundos y Edmonds-Karp 0,114; es 7,6 veces más rápido.
>
> Por el teorema max-flow/min-cut, el corte mínimo tiene la misma capacidad. Encontramos 168 aristas en el corte. Las mayores son salidas de Binance 1, Poloniex 4, Binance 4, Bitmax 3 y Huobi hacia billeteras que no tienen ruta hacia FTX. El cuello de botella no es una sola tubería: es un conjunto de contrapartes que absorben liquidez sin retorno.
>
> La sensibilidad muestra que Binance 1 a Huobi 5 alcanza 89,4 millones, más que a FTX. La capacidad depende de las rutas disponibles. Eso sí: son capacidades acumuladas de 19 meses, no instantáneas; el resultado es una cota estructural, no una predicción diaria.”

**En pantalla:** barra del corte mínimo y tabla de sensibilidad.

---

## 8:25–8:50 — Cierre (Emerson Ballesteros Diaz o todo el grupo)

**Pantalla:** tabla comparativa global y conclusiones.

**Narración:**
> “En síntesis: la red USDC está fragmentada y es frágil; la importancia de un exchange no es solo su volumen; existen 13 comunidades de liquidez con estructura de hub-and-spoke; y la capacidad máxima está limitada por contrapartes, no solo por exchanges.
>
> Todo el código, los datos compactos y las instrucciones para ejecutarlo en Colab están en el notebook y en el repositorio. No usamos Dijkstra en ninguna tarea. Gracias.”

---

## Checklist de grabación

- [ ] Duración total ≤ 9:00 (cronómetro visible o edición).
- [ ] Mostrar la portada, la tabla de tareas y el badge “sin Dijkstra”.
- [ ] Mostrar al menos una figura por tarea.
- [ ] Decir el nombre de cada integrante y la tarea que presenta.
- [ ] Mostrar el resultado numérico principal de cada tarea.
- [ ] Cerrar con el repositorio y el enlace del notebook.
- [ ] Audio claro; evitar ruido de fondo.
- [ ] Subir a YouTube como “no listado” o “público” y pegar el enlace en el README.
