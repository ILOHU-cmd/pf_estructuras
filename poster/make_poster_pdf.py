#!/usr/bin/env python3
"""Genera una versión PDF sintética del poster (A1 vertical) con ReportLab."""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A1
from reportlab.lib.colors import HexColor, white
from reportlab.lib.utils import ImageReader, simpleSplit

ROOT = Path(__file__).resolve().parent
FIG = ROOT / "figs"
OUT = ROOT / "poster.pdf"

W, H = A1  # 594 x 841 mm en puntos
M = 34
INK = HexColor("#10231f")
MUTED = HexColor("#52645f")
TEAL = HexColor("#0b5d4b")
TEAL2 = HexColor("#12836b")
GOLD = HexColor("#c9972c")
RED = HexColor("#b23a48")
BLUE = HexColor("#2d5f9a")
PAPER = HexColor("#f7f5ef")
CARD = HexColor("#fffdf8")
LINE = HexColor("#d8d2c4")


def para(c, text, x, y, width, size=11, leading=14, color=INK, font="Helvetica"):
    c.setFillColor(color)
    c.setFont(font, size)
    for line in simpleSplit(text, font, size, width):
        c.drawString(x, y, line)
        y -= leading
    return y


def bullets(c, items, x, y, width, size=10.5, leading=13.5, color=INK):
    for item in items:
        c.setFillColor(TEAL2)
        c.circle(x + 3, y + 3, 2.2, fill=1, stroke=0)
        y = para(c, item, x + 12, y, width - 12, size=size, leading=leading, color=color)
        y -= 2
    return y


def card(c, x, y, w, h, number, title):
    c.setFillColor(CARD)
    c.setStrokeColor(LINE)
    c.setLineWidth(1.0)
    c.roundRect(x, y, w, h, 10, fill=1, stroke=1)
    c.setFillColor(TEAL)
    c.circle(x + 24, y + h - 26, 13, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(x + 24, y + h - 30, str(number))
    c.setFillColor(TEAL)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(x + 46, y + h - 31, title)


def image(c, path, x, y, w, h):
    if not path.exists():
        return
    img = ImageReader(str(path))
    iw, ih = img.getSize()
    scale = min(w / iw, h / ih)
    dw, dh = iw * scale, ih * scale
    c.drawImage(str(path), x + (w - dw) / 2, y + (h - dh) / 2, dw, dh,
                preserveAspectRatio=True, mask="auto")


def kpis(c, x, y, w, items):
    bw = (w - 2 * 8) / 3
    for i, (big, small) in enumerate(items):
        bx = x + i * (bw + 8)
        c.setFillColor(HexColor("#e7f2ee"))
        c.setStrokeColor(HexColor("#b9d8ce"))
        c.roundRect(bx, y, bw, 54, 7, fill=1, stroke=1)
        c.setFillColor(TEAL)
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(bx + bw / 2, y + 30, big)
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 8)
        c.drawCentredString(bx + bw / 2, y + 14, small)
    return y - 12


# ---------------------------------------------------------------------------
c = canvas.Canvas(str(OUT), pagesize=A1)
c.setFillColor(PAPER)
c.rect(0, 0, W, H, fill=1, stroke=0)

# Header
c.setFillColor(TEAL)
c.rect(0, H - 150, W, 150, fill=1, stroke=0)
c.setFillColor(HexColor("#cfe4dc"))
c.setFont("Helvetica-Bold", 11)
c.drawString(M, H - 38, "PROYECTO FINAL · TEORÍA DE GRAFOS · UNIVERSIDAD INDUSTRIAL DE SANTANDER")
c.setFillColor(white)
c.setFont("Helvetica-Bold", 34)
c.drawString(M, H - 82, "La red de transferencias Ethereum: fragmentación, poder y liquidez")
c.setFillColor(HexColor("#d8ece5"))
c.setFont("Helvetica", 13)
c.drawString(M, H - 108, "Cuatro lecturas algorítmicas de 38,9 millones de transferencias ERC-20 (2018–2020)")
c.setFont("Helvetica", 10.5)
c.drawString(M, H - 130, "Emerson Ballesteros Diaz · T1   |   Jhon Arciniegas · T2   |   Pablo Alvarez · T3   |   Todo el grupo · T4")

# Badge no Dijkstra
c.setFillColor(white)
c.setStrokeColor(RED)
c.setLineWidth(2)
c.roundRect(W - M - 130, H - 138, 130, 95, 8, fill=1, stroke=1)
c.setFillColor(RED)
c.setFont("Helvetica-Bold", 17)
c.drawCentredString(W - M - 65, H - 80, "SIN")
c.drawCentredString(W - M - 65, H - 101, "Dijkstra")
c.setFillColor(MUTED)
c.setFont("Helvetica", 7.5)
c.drawCentredString(W - M - 65, H - 122, "algoritmos propios")

# Dataset strip
top = H - 180
c.setFillColor(CARD)
c.setStrokeColor(LINE)
c.roundRect(M, top - 175, W - 2 * M, 175, 10, fill=1, stroke=1)
c.setFillColor(TEAL)
c.setFont("Helvetica-Bold", 17)
c.drawString(M + 18, top - 28, "Dataset y preprocesamiento")
c.setFillColor(INK)
y = top - 50
y = para(c, "38.901.039 transferencias ERC-20 · 28 tokens · 6,08 millones de direcciones únicas · bloques 6.525.201–10.000.000 (oct. 2018 – may. 2020). "
           "Se usan USDC y DAI para normalizar valor a USD; se excluyen mint/burn (0x000…), auto-loops y valores no positivos. "
           "Volumen stablecoin total: USD 60.302 M; volumen en el grafo de exchanges: USD 16.347 M. "
           "El CSV original pesa 8,3 GB; el notebook usa 32 MB de datos compactos generados con preprocess.py.",
         M + 18, y, W - 2 * M - 36, size=11, leading=14)
kpis(c, M + 18, top - 145, W - 2 * M - 36, [
    ("4.326.261", "transferencias stablecoin"),
    ("USD 16.347 M", "volumen en grafo de exchanges"),
    ("296", "exchanges (247 CEX / 49 DEX)"),
])

# Two columns of task cards
col_w = (W - 2 * M - 24) / 2
x1, x2 = M, M + col_w + 24
row_h = 660
gap = 20
top_row = top - 200
bot_row = top_row - row_h - gap

# T1
y = top_row - row_h
card(c, x1, y, col_w, row_h, 1, "Fragmentación y puntos críticos")
yy = y + row_h - 58
yy = para(c, "Problema: ¿qué direcciones pueden aislar la liquidez USDC? Modelo: grafo no dirigido G=(V,E); "
             "vértices = direcciones, aristas = transferencias. Componente = islote de liquidez; punto de articulación = nodo cuyo fallo parte la red.",
         x1 + 20, yy, col_w - 40, size=10.5, leading=13)
image(c, FIG / "cell11_0.png", x1 + 20, yy - 265, col_w - 40, 250)
kpis(c, x1 + 20, yy - 330, col_w - 40, [
    ("36.618", "componentes"), ("28.587", "puntos de articulación"), ("141.674", "puentes"),
])
bullets(c, [
    "Componente gigante: 110.596 vértices (56,9 %). El resto son islotes: red global pero fragmentada.",
    "Binance 1: al eliminarlo se separan 19.447 vértices. Los exchanges son cuellos de botella estructurales.",
    "Algoritmos: Union-Find + BFS para componentes; Tarjan iterativo para articulaciones y puentes. Validado contra fuerza bruta.",
], x1 + 20, yy - 365, col_w - 40, size=9.5, leading=12)

# T2
card(c, x2, y, col_w, row_h, 2, "Importancia sistémica: PageRank")
yy = y + row_h - 58
yy = para(c, "Modelo: grafo dirigido y ponderado por volumen USD; exchanges + 2.000 contrapartes. "
             "PageRank mide la probabilidad estacionaria de un paseo aleatorio con reinicio (d=0,85).",
         x2 + 20, yy, col_w - 40, size=10.5, leading=13)
image(c, FIG / "cell16_1.png", x2 + 20, yy - 265, col_w - 40, 250)
kpis(c, x2 + 20, yy - 330, col_w - 40, [
    ("0,0904", "Binance 1"), ("0,0755", "1inch"), ("0,0735", "OasisDEX"),
])
bullets(c, [
    "Binance 1 lidera; 1inch y OasisDEX tienen una posición topológica desproporcionada respecto a su volumen.",
    "Comparación: PageRank ponderado vs. no ponderado (Spearman 0,679) y vs. in-strength (0,839; top-20: 17/20).",
    "El volumen explica mucho, pero no todo: la conectividad y la dirección de los flujos cambian el ranking.",
], x2 + 20, yy - 365, col_w - 40, size=9.5, leading=12)

# T3
y = bot_row - row_h
card(c, x1, y, col_w, row_h, 3, "Comunidades de liquidez: Louvain")
yy = y + row_h - 58
yy = para(c, "Modelo: grafo no dirigido ponderado por frecuencia de transferencias (no por volumen). "
             "Louvain maximiza la modularidad Q con movimiento local + agregación y 10 reinicios.",
         x1 + 20, yy, col_w - 40, size=10.5, leading=13)
image(c, FIG / "cell21_1.png", x1 + 20, yy - 300, col_w - 40, 285)
kpis(c, x1 + 20, yy - 365, col_w - 40, [
    ("13", "comunidades"), ("0,614", "modularidad Q"), ("24", "comunidades LP"),
])
bullets(c, [
    "Comunidad mayor: ecosistema Binance (1.346 nodos); luego 1inch, FTX, OasisDEX, Bitfinex/KuCoin y HitBTC.",
    "Label Propagation: Q=0,605 con 24 comunidades; Louvain logra una partición más compacta y con mayor Q.",
    "Proyección exchange–exchange: solo 88 de 296 exchanges comparten contrapartes principales (6 comunidades, Q=0,149).",
], x1 + 20, yy - 400, col_w - 40, size=9.5, leading=12)

# T4
card(c, x2, y, col_w, row_h, 4, "Flujo máximo y cuellos de botella")
yy = y + row_h - 58
yy = para(c, "Modelo: red dirigida con capacidades c(u,v) = volumen USD agregado. Origen Binance 1, destino FTX. "
             "Por max-flow/min-cut, el flujo máximo es la capacidad del corte mínimo.",
         x2 + 20, yy, col_w - 40, size=10.5, leading=13)
image(c, FIG / "cell26_0.png", x2 + 20, yy - 265, col_w - 40, 250)
kpis(c, x2 + 20, yy - 330, col_w - 40, [
    ("USD 56,85 M", "flujo máximo"), ("168", "aristas en el corte"), ("7,6×", "Dinic vs. EK"),
])
bullets(c, [
    "Dinic y Edmonds-Karp coinciden: USD 56,85 M, 216 aumentos. Dinic ≈0,015 s vs. EK ≈0,114 s.",
    "El corte está dominado por salidas hacia billeteras que absorben flujo sin retorno; no es una sola tubería.",
    "Sensibilidad: Binance 1 → Huobi 5 alcanza USD 89,4 M. Capacidades acumuladas de 19 meses, no instantáneas.",
], x2 + 20, yy - 365, col_w - 40, size=9.5, leading=12)

# Comparison panel (fills the lower area)
panel_top = (bot_row - row_h) - 24
panel_bottom = 190
panel_h = panel_top - panel_bottom
c.setFillColor(CARD)
c.setStrokeColor(LINE)
c.setLineWidth(1.0)
c.roundRect(M, panel_bottom, W - 2 * M, panel_h, 10, fill=1, stroke=1)
c.setFillColor(TEAL)
c.setFont("Helvetica-Bold", 17)
c.drawString(M + 18, panel_top - 28, "Comparación global, validación y limitaciones")

# Table
table_x = M + 18
table_y = panel_top - 58
table_w = W - 2 * M - 36
col_widths = [105, 390, 430, table_w - 105 - 390 - 430]
headers = ["Tarea", "Modelo de grafo", "Algoritmo propio", "Resultado principal"]
row_heights = [30, 64, 64, 64, 64]
rows = [
    ["T1", "No dirigido, no ponderado; V = direcciones USDC", "Union-Find + Tarjan iterativo", "36.618 componentes; 28.587 puntos de articulación; 141.674 puentes"],
    ["T2", "Dirigido, ponderado por volumen USD", "PageRank por iteración de potencias", "Binance 1 (0,0904), 1inch (0,0755) y OasisDEX (0,0735)"],
    ["T3", "No dirigido, ponderado por frecuencia", "Louvain multi-nivel + 10 reinicios", "13 comunidades; Q ≈ 0,614; ecosistema Binance de 1.346 nodos"],
    ["T4", "Dirigido, capacidades en USD", "Dinic (flujo bloqueante)", "Flujo máximo USD 56,85 M; corte de 168 aristas; Dinic 7,6× más rápido que EK"],
]
# Header row
xx = table_x
for j, htxt in enumerate(headers):
    c.setFillColor(HexColor("#e7f2ee"))
    c.rect(xx, table_y - row_heights[0], col_widths[j], row_heights[0], fill=1, stroke=1)
    c.setFillColor(TEAL)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(xx + 5, table_y - row_heights[0] + 10, htxt)
    xx += col_widths[j]
table_y -= row_heights[0]
for i, row in enumerate(rows):
    xx = table_x
    rh = row_heights[i + 1]
    if i % 2 == 0:
        c.setFillColor(HexColor("#fbfaf5"))
        c.rect(table_x, table_y - rh, table_w, rh, fill=1, stroke=0)
    for j, txt in enumerate(row):
        c.setStrokeColor(LINE)
        c.rect(xx, table_y - rh, col_widths[j], rh, fill=0, stroke=1)
        c.setFillColor(INK if j else TEAL)
        c.setFont("Helvetica-Bold" if j == 0 else "Helvetica", 8.2)
        yy = table_y - 14
        for line in simpleSplit(txt, "Helvetica-Bold" if j == 0 else "Helvetica", 8.2, col_widths[j] - 10):
            c.drawString(xx + 5, yy, line)
            yy -= 10.5
        xx += col_widths[j]
    table_y -= rh

# Validation / limitations bullets
by = table_y - 28
c.setFillColor(TEAL)
c.setFont("Helvetica-Bold", 12)
c.drawString(table_x, by, "Validación cruzada")
c.setFillColor(INK)
bullets(c, [
    "DSU y BFS producen exactamente las mismas componentes.",
    "Tarjan coincide con fuerza bruta en un subgrafo BFS de 300 nodos.",
    "Dinic y Edmonds-Karp obtienen el mismo flujo máximo.",
    "Louvain se compara con Label Propagation y particiones triviales.",
], table_x, by - 22, col_widths[0] + col_widths[1] - 10, size=9.2, leading=12)

c.setFillColor(TEAL)
c.setFont("Helvetica-Bold", 12)
c.drawString(table_x + col_widths[0] + col_widths[1] + 16, by, "Limitaciones")
c.setFillColor(INK)
bullets(c, [
    "Dataset agregado sin timestamps: no se modela el orden temporal.",
    "Liquidez restringida a USDC/DAI; faltan precios históricos de otros tokens.",
    "Etiquetas de exchanges incompletas; muchas billeteras sin identificar.",
    "Capacidades acumuladas de 19 meses, no instantáneas; Louvain es heurístico.",
], table_x + col_widths[0] + col_widths[1] + 16, by - 22, table_w - col_widths[0] - col_widths[1] - 16, size=9.2, leading=12)

# Footer conclusions
fy = 105
c.setFillColor(TEAL)
c.rect(M, fy, W - 2 * M, 72, fill=1, stroke=0)
c.setFillColor(white)
c.setFont("Helvetica-Bold", 15)
c.drawString(M + 16, fy + 46, "Conclusiones")
c.setFont("Helvetica", 10)
c.drawString(M + 16, fy + 25, "Red fragmentada y frágil · importancia más allá del volumen · 13 ecosistemas de liquidez · capacidad limitada por contrapartes, no solo por exchanges.")
c.setFont("Helvetica", 8.5)
c.drawString(M + 16, fy + 8, "Método: DSU/BFS/Tarjan, PageRank, Louvain/LP y Dinic/EK implementados desde cero y validados entre sí. Sin Dijkstra.")

# Bottom references
c.setFillColor(MUTED)
c.setFont("Helvetica", 7.5)
c.drawString(M, 82, "Referencias: Tarjan (1972) · Page et al. (1999) · Blondel et al. (2008) · Dinic (1970) · Edmonds & Karp (1972) · Raghavan et al. (2007) · ERC-20 (Ethereum EIPs).")
c.drawString(M, 68, "Recursos: proyecto_grafos_ethereum.ipynb · preprocess.py · data/ · poster/poster.html")
c.setStrokeColor(LINE)
c.line(M, 54, W - M, 54)
c.setFont("Helvetica", 7.5)
c.drawString(M, 38, "Universidad Industrial de Santander · Teoría de Grafos · Proyecto final 2026 · Entregables: notebook (70 %), video ≤ 9 min (15 %), poster (15 %).")
c.drawRightString(W - M, 38, "QR / enlace: video y notebook")

c.showPage()
c.save()
print("PDF generado:", OUT, OUT.stat().st_size, "bytes")
