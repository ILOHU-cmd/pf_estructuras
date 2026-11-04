# Datos compactos

Estos archivos se generan con `../preprocess.py` a partir de
`../ethereum-exchanges/token_transfers_full.csv` y las etiquetas de exchanges.

| Archivo | Filas aprox. | Descripción |
|---|---:|---|
| `stablecoin_flows.csv` | 6.739 | Flujos agregados en USD entre exchanges y sus 2.000 contrapartes principales |
| `exchange_direct_flows.csv` | 107 | Solo flujos exchange → exchange |
| `exchange_shared_wallets.csv` | 1.213 | Proyección exchange–exchange por billeteras compartidas |
| `usdc_sample.csv` | 300.647 | Muestra de transferencias USDC para la Tarea 1 |
| `monthly_transfers.csv` | 19 | Serie mensual de transferencias y volumen stablecoin |
| `token_counts.csv` | 28 | Conteo por contrato de token |
| `exchange_labels.csv` | 296 | Etiquetas normalizadas de exchanges |
| `summary.json` | — | Resumen global y metadatos del preprocesamiento |

## Columnas principales

### `stablecoin_flows.csv`

`src, dst, src_name, dst_name, src_type, dst_type, volume_usd, n_transfers, tokens`

- `src`, `dst`: direcciones Ethereum normalizadas a minúsculas.
- `src_type`, `dst_type`: `cex`, `dex` o `wallet`.
- `volume_usd`: volumen agregado en dólares (USDC/DAI normalizados).
- `n_transfers`: número de transferencias agregadas.
- `tokens`: stablecoins involucradas (`USDC`, `DAI`).

### `usdc_sample.csv`

`from_address, to_address, value, block_number`

### `monthly_transfers.csv`

`month, n_transfers, n_stablecoin, stablecoin_volume_usd`

### `summary.json`

Incluye conteos globales, rango de bloques, número de exchanges, contrapartes,
filas generadas y tamaño de la muestra USDC.

> El CSV original de 8,3 GB no se incluye en esta carpeta para mantener el
> repositorio liviano y compatible con Google Colab.
