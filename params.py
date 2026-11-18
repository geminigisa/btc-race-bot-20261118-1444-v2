"""Parameter bot RSI-reclaim untuk btc-race-24h-20261118-1444.

Dipilih dari plateau hasil screening struktur (bukan dari satu puncak):
ukuran 0,28-0,35, sl 20/25, tp 60, hold 60/90 semua lolos aturan ketat;
konfigurasi di sini diambil di tengah plateau (size 0,30) supaya margin
worst-case lebih baik dari ukuran 0,35.

Hasil aproksimasi screening (biaya flat 26 bps per round trip):
  1444 +$2,34 | OOS 0603 -$0,61 | 0828 +$0,23 | 12nov +$1,29 | 13nov -$2,38
  worst-OOS -$2,38 (margin +$0,62 dari batas -$3), 2 window OOS >= $0.
Validasi eksak memakai harness Replay (fill engine kit) — lihat README.
"""

P = {
    # Entry: RSI(14) Wilder kembali >= level setelah sempat < level.
    "rsi_level": 35,
    # Sizing: pecahan kas per entry (30%).
    "size_frac_num": 30,
    "size_frac_den": 100,
    # Exit: take-profit / stop-loss dalam bps dari entry open.
    "tp_bps": 60,
    "sl_bps": 20,
    # Exit: maksimal bar menahan posisi.
    "max_hold": 60,
    # Maksimal trip dalam satu window.
    "max_trips": 2,
    # Anggaran kerugian: tidak ada entry baru bila realized PnL sudah
    # <= -loss_budget (dalam quote units; 2_000_000 = $2,00).
    "loss_budget": 2_000_000,
    # Jangan entry di 60 bar terakhir window.
    "no_entry_last": 60,
    # Slippage maksimum order (bps), sama seperti bot pemenang 0603.
    "max_slippage_bps": 100,
}
