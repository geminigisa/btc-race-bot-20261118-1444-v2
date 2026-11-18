# BTC Race Bot — RSI Reclaim (btc-race-24h-20261118-1444)

[![make.fun · btc-race-24h-20261118-1444](https://make.fun/badge/btc-race-24h-20261118-1444.svg)](https://make.fun/bounty/btc-race-24h-20261118-1444?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444)
[![rank](https://make.fun/badge/btc-race-24h-20261118-1444/geminigisa/btc-race-bot-20261118-1444-v2/rank.svg)](https://make.fun/bounty/btc-race-24h-20261118-1444/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444)
[![reward](https://make.fun/badge/btc-race-24h-20261118-1444/geminigisa/btc-race-bot-20261118-1444-v2/reward.svg)](https://make.fun/bounty/btc-race-24h-20261118-1444?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444)

Bot trading CBBTC/USDC, long-only, paper $1.000, 24 jam (1440 bar 1 menit).
Entry untuk kompetisi make.fun `btc-race-24h-20261118-1444`.

## Strategi

**RSI reclaim, bukan dip-buy.** Entry hanya saat RSI(14) Wilder kembali
menembus ke atas 35 setelah sempat di bawah 35 — pantulan yang sudah
dikonfirmasi momentum. Sizing 30% kas per entry, maksimal 2 trip per
window, dengan anggaran kerugian: tidak ada entry baru bila realized PnL
sudah <= -$2,00.

Exit (yang mana dulu tercapai, diukur dari open bar saat buy terisi):
- take-profit +60 bps
- stop-loss -20 bps
- max hold 60 bar

## Kenapa struktur ini

Bot dip-buy pemenang race 0603 (entry saat close turun >= dip_bps dari
max 45 bar lalu memantul, 100% kas, 1 trip) di dev window 1444 (pasar
turun -280 bps) rugi -$6,10 — gagal dev gate. Tuning 3.888 + 426 varian
parameter bot itu menghasilkan 0 yang lolos aturan ketat (dev > $0,
worst-OOS >= -$3, >= 2 window OOS >= $0). Wawasan kunci: dengan size
100%, satu trip kena stop-loss saja sudah -$4,60..-$6,60, jadi
worst-OOS >= -$3 mustahil secara matematis. Yang harus berubah adalah
SIZE dan loss budget, bukan parameter entry/exit.

Screening 6 struktur (RSI reclaim, V-shape, Bollinger + RSI, breakout)
menunjukkan RSI reclaim satu-satunya yang menghasilkan uang di 1444.
Grid fokus 486 kombinasi pada struktur ini menghasilkan 16 yang lolos
aturan ketat — semuanya membentuk plateau, bukan satu puncak. Konfigurasi
di `params.py` diambil di tengah plateau.

## Hasil

Aproksimasi screening (biaya flat 26 bps/round trip):
1444 +$2,34 | OOS 0603 -$0,61 | 0828 +$0,23 | 12nov +$1,29 | 13nov -$2,38
(worst-OOS -$2,38; 2 window OOS >= $0).

Validasi eksak dengan `harness.Replay` (fill engine kit, bukan aproksimasi)
dan hasilnya ada di `STRATEGY.md`.

## Menjalankan

```sh
python3 -P -s main.py < batch.ndjson > replies.ndjson
```

Stdlib only, deterministik penuh (tanpa jam dinding, random, network,
atau file). Protokol: `agent-fun/bars-replay/v1` via shim `vendor/`
(salinan byte-identical dari `sdk/makefun_bars.py` kit kompetisi).

## Lisensi

MIT — lihat `LICENSE`.
