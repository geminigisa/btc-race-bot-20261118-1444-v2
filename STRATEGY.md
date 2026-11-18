# Strategi — BTC Race Bot RSI Reclaim (btc-race-24h-20261118-1444)

## Desain

Long-only CBBTC/USDC, 30% kas per entry, maksimal 2 trip per window 1440 bar.
Entry hanya saat RSI(14) Wilder kembali menembus ke atas 35 setelah sempat
di bawah 35 ("RSI reclaim"): pantulan yang sudah dikonfirmasi momentum,
bukan sekadar harga turun dari tertinggi.

Exit (yang mana dulu tercapai, diukur dari open bar saat buy terisi):
take-profit +60 bps, stop-loss -20 bps, max hold 60 bar. Anggaran
kerugian: tidak ada entry baru bila realized PnL sudah <= -$2,00.

## Kenapa bukan dip-buy

Bot dip-buy pemenang race 0603 (100% kas, 1 trip) di dev window 1444
(pasar turun -280 bps) rugi -$6,10. Tuning 3.888 + 426 varian parameter
bot itu menghasilkan 0 yang lolos aturan ketat. Wawasan kunci: dengan
size 100%, satu trip kena stop-loss saja sudah -$4,60..-$6,60, jadi
worst-OOS >= -$3 mustahil secara matematis. Yang harus berubah adalah
SIZE dan loss budget, bukan parameter entry/exit. Screening 6 struktur
menunjukkan RSI reclaim satu-satunya yang menghasilkan uang di 1444;
grid 486 kombinasi menghasilkan plateau 16 konfigurasi yang lolos —
yang dipakai di sini diambil di tengah plateau (size 0,30).

## Hasil eksak (harness Replay, fill engine kit — bukan aproksimasi)

| Window | Net PnL | Trades | Max DD |
|--------|---------|--------|--------|
| 1444 (dev) | +$2,7592 | 4 (2 trip: +$1,2868, +$1,4724) | 0,063% |
| 0603 (OOS) | -$0,1968 | 4 (2 trip: +$1,2273, -$1,4241) | 0,171% |
| 0828 (OOS) | +$0,5731 | 4 (2 trip: +$1,2433, -$0,6703) | 0,091% |
| 12nov (OOS) | +$1,8288 | 4 (2 trip: +$2,9939, -$1,1651) | 0,134% |
| 13nov (OOS) | -$2,0418 | 2 (1 trip: -$2,0418; loss budget memblokir trip ke-2) | 0,274% |

Gate ketat: dev 1444 +$2,76 > $0 (PASS), worst-OOS -$2,04 >= -$3 (PASS,
margin +$0,96), 2 window OOS >= $0 (0828, 12nov — PASS). 0 order ditolak
di semua window. Determinisme: 2x run pada data identik menghasilkan
action log byte-identical (reply sha 3e057147... di 1444, f80d8db3... di
13nov). Input malformed (batch tanpa bar / bar simbol lain) dijawab
dengan orders kosong, tanpa crash. Tidak ada lookahead: keputusan hanya
memakai bar yang sudah tutup sampai batch saat itu.
