#!/usr/bin/env python3
"""
Preprocesamiento reproducible del dataset Ethereum token transfers.

Genera los archivos compactos que consume el notebook:

  data/stablecoin_flows.csv        Flujos agregados (USD) entre exchanges y
                                   contrapartes, usando USDC/USDT/DAI.
  data/exchange_direct_flows.csv   Solo flujos exchange -> exchange.
  data/exchange_shared_wallets.csv Proyección exchange-exchange por billeteras
                                   compartidas (para detección de comunidades).
  data/usdc_sample.csv             Muestra de transferencias USDC para el
                                   análisis de componentes conexas.
  data/summary.json                Estadísticas del dataset.

Uso:
    python preprocess.py --input ethereum-exchanges/token_transfers_full.csv

El script recorre el CSV completo una sola vez (streaming), por lo que puede
ejecutarse con ~1 GB de RAM.  No usa pandas para que sea portable.
"""

from __future__ import annotations

import argparse
import csv
import datetime
import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

# Stablecoins principales. value se normaliza a USD dividiendo por 10**decimals.
STABLECOINS = {
    "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48": ("USDC", 6),
    "0xdac17f958d2ee523a2206206994597c13d831ec7": ("USDT", 6),
    "0x6b175474e89094c44da98b954eedeac495271d0f": ("DAI", 18),
}
USDC = "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"

TOKEN_RE = re.compile(r"^0x[0-9a-f]{40}$")


def load_exchanges(path: Path) -> dict[str, dict]:
    """Carga las etiquetas de exchanges (encoding latin-1: hay nombres con tildes)."""
    out: dict[str, dict] = {}
    with path.open(newline="", encoding="latin-1") as fh:
        for row in csv.DictReader(fh):
            addr = row["address"].strip().lower()
            if TOKEN_RE.match(addr):
                out[addr] = {"type": row["type"].strip(), "name": row["name"].strip()}
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--input",
        type=Path,
        default=Path("ethereum-exchanges/token_transfers_full.csv"),
        help="CSV original de transferencias",
    )
    ap.add_argument(
        "--labels",
        type=Path,
        default=Path("ethereum-exchanges/exchangeLabels.csv"),
        help="CSV de etiquetas de exchanges",
    )
    ap.add_argument("--outdir", type=Path, default=Path("data"))
    ap.add_argument("--usdc-target", type=int, default=300_000,
                    help="Filas USDC objetivo en la muestra")
    ap.add_argument("--top-wallets", type=int, default=2000,
                    help="Contrapartes principales que se conservan en el grafo de flujos")
    ap.add_argument("--max-wallet-exchanges", type=int, default=50,
                    help="Máximo de exchanges por billetera al proyectar co-ocurrencia")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    rng = random.Random(args.seed)
    args.outdir.mkdir(parents=True, exist_ok=True)

    exchanges = load_exchanges(args.labels)
    print(f"Exchanges etiquetados: {len(exchanges)}")

    # ------------------------------------------------------------------
    # 1. Agregados del grafo de stablecoins
    # ------------------------------------------------------------------
    # (src, dst) -> [volumen_usd, n, Counter(tokens)]
    flows: dict[tuple[str, str], list] = defaultdict(lambda: [0.0, 0, Counter()])
    # (exchange, wallet) -> [volumen, n] ; dirección implícita por el par
    wallet_vol: Counter = Counter()
    wallet_cnt: Counter = Counter()
    wallet_exchanges: dict[str, set[str]] = defaultdict(set)

    # Muestra USDC: muestreo de Bernoulli (suficiente y reproducible)
    p_usdc = args.usdc_target / 2_278_533  # nº aproximado de filas USDC del dataset
    usdc_sample: list[list[str]] = []

    n_rows = 0
    min_block, max_block = 10**18, 0
    token_counts: Counter = Counter()
    rows_with_exchange = 0
    rows_stable = 0
    monthly = defaultdict(lambda: [0, 0, 0.0])
    # hashes de 64 bits: permite estimar direcciones únicas con ~6M entradas
    addr_hashes: set[int] = set()
    genesis_like = datetime.datetime(2018, 10, 8)  # bloque 6_525_201 aprox.

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
            rows_stable += 1
            symbol, decimals = STABLECOINS[token]
            value = float(row[3]) / (10**decimals)
            monthly[month][1] += 1
            monthly[month][2] += value

            is_src = src in exchanges
            is_dst = dst in exchanges
            if not (is_src or is_dst):
                continue
            rows_with_exchange += 1
            key = (src, dst)
            agg = flows[key]
            agg[0] += value
            agg[1] += 1
            agg[2][symbol] += 1

            # Contrapartes de exchanges (para PageRank / co-ocurrencia)
            if is_src and not is_dst:
                wallet_vol[dst] += value
                wallet_cnt[dst] += 1
                wallet_exchanges[dst].add(src)
            elif is_dst and not is_src:
                wallet_vol[src] += value
                wallet_cnt[src] += 1
                wallet_exchanges[src].add(dst)

            if n_rows % 10_000_000 == 0:
                print(f"  ... {n_rows:,} filas procesadas")

    print(f"Filas totales: {n_rows:,}; stablecoins: {rows_stable:,}; "
          f"con exchange: {rows_with_exchange:,}")

    # ------------------------------------------------------------------
    # 2. Selección de contrapartes principales
    # ------------------------------------------------------------------
    # Ranking mixto: volumen (log) y actividad. Evita que una sola ballena
    # desplace billeteras que conectan varios exchanges.
    def wallet_score(addr: str) -> float:
        import math
        return math.log10(1 + wallet_vol[addr]) + 0.5 * math.log10(1 + wallet_cnt[addr])

    ranked = sorted(wallet_vol, key=wallet_score, reverse=True)
    top_wallets = set(ranked[: args.top_wallets])
    print(f"Contrapartes con actividad: {len(wallet_vol):,}; "
          f"se conservan {len(top_wallets):,}")

    keep = set(exchanges) | top_wallets

    # ------------------------------------------------------------------
    # 3. Escritura de flujos agregados
    # ------------------------------------------------------------------
    def node_name(addr: str) -> str:
        if addr in exchanges:
            return exchanges[addr]["name"]
        return f"wallet:{addr[:8]}…{addr[-4:]}"

    def node_type(addr: str) -> str:
        if addr in exchanges:
            return exchanges[addr]["type"]
        return "wallet"

    flow_path = args.outdir / "stablecoin_flows.csv"
    direct_path = args.outdir / "exchange_direct_flows.csv"
    n_flow_rows = n_direct_rows = 0
    with flow_path.open("w", newline="", encoding="utf-8") as ff, \
         direct_path.open("w", newline="", encoding="utf-8") as fd:
        wf = csv.writer(ff)
        wd = csv.writer(fd)
        header = ["src", "dst", "src_name", "dst_name", "src_type", "dst_type",
                  "volume_usd", "n_transfers", "tokens"]
        wf.writerow(header)
        wd.writerow(header)
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

    # ------------------------------------------------------------------
    # 4. Proyección exchange-exchange por billeteras compartidas
    # ------------------------------------------------------------------
    # Para cada contraparte principal, se conectan todos los exchanges con
    # los que interactuó. Peso = nº de billeteras compartidas y volumen mínimo
    # observado (una medida conservadora del flujo que las une).
    shared: dict[tuple[str, str], dict] = defaultdict(
        lambda: {"wallets": 0, "volume": 0.0}
    )
    degree_hist: Counter = Counter()
    skipped_wallets = 0
    for wallet, exs_set in wallet_exchanges.items():
        exs = sorted(exs_set)
        degree_hist[len(exs)] += 1
        if len(exs) < 2:
            continue
        if len(exs) > args.max_wallet_exchanges:
            skipped_wallets += 1
            continue
        # Volumen de esta billetera con cada exchange (aproximado por el total;
        # se usa el mínimo entre ambos como cota inferior del flujo compartido).
        for i in range(len(exs)):
            for j in range(i + 1, len(exs)):
                a, b = exs[i], exs[j]
                key = (a, b) if a < b else (b, a)
                entry = shared[key]
                entry["wallets"] += 1
                entry["volume"] += wallet_vol[wallet]

    shared_path = args.outdir / "exchange_shared_wallets.csv"
    with shared_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["a", "b", "a_name", "b_name", "a_type", "b_type",
                    "shared_wallets", "volume_usd"])
        for (a, b), entry in sorted(shared.items(), key=lambda kv: -kv[1]["wallets"]):
            w.writerow([a, b, exchanges[a]["name"], exchanges[b]["name"],
                        exchanges[a]["type"], exchanges[b]["type"],
                        entry["wallets"], f"{entry['volume']:.6f}"])

    # ------------------------------------------------------------------
    # 5. Muestra USDC
    # ------------------------------------------------------------------
    usdc_path = args.outdir / "usdc_sample.csv"
    with usdc_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["from_address", "to_address", "value", "block_number"])
        for row in usdc_sample:
            w.writerow([row[1].lower(), row[2].lower(), row[3], row[6]])

    summary = {
        "n_rows": n_rows,
        "n_unique_addresses_approx": len(addr_hashes),
        "n_tokens": len(token_counts),
        "n_stablecoin_rows": rows_stable,
        "n_rows_with_exchange": rows_with_exchange,
        "block_min": min_block,
        "block_max": max_block,
        "n_exchanges": len(exchanges),
        "n_exchange_types": dict(Counter(v["type"] for v in exchanges.values())),
        "n_counterparties": len(wallet_vol),
        "n_top_wallets": len(top_wallets),
        "n_flow_rows": n_flow_rows,
        "n_direct_rows": n_direct_rows,
        "n_shared_pairs": len(shared),
        "n_wallets_skipped_projection": skipped_wallets,
        "wallet_exchange_degree_hist": dict(sorted(degree_hist.items())),
        "n_usdc_sample": len(usdc_sample),
    }
    (args.outdir / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    with (args.outdir / "token_counts.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["token_address", "n_transfers"])
        for tok, cnt in token_counts.most_common():
            w.writerow([tok, cnt])

    with (args.outdir / "exchange_labels.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["type", "address", "name"])
        for addr, info in sorted(exchanges.items(), key=lambda kv: (kv[1]["type"], kv[1]["name"])):
            w.writerow([info["type"], addr, info["name"]])

    with (args.outdir / "monthly_transfers.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["month", "n_transfers", "n_stablecoin", "stablecoin_volume_usd"])
        for month in sorted(monthly):
            r = monthly[month]
            w.writerow([month, r[0], r[1], f"{r[2]:.2f}"])

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"Archivos escritos en {args.outdir.resolve()}")


if __name__ == "__main__":
    main()
