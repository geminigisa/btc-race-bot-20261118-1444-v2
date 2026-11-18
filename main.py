"""Bot trading RSI-reclaim untuk kompetisi make.fun "Race a BTC trading bot"
(btc-race-24h-20261118-1444).

Strategi (struktural berbeda dari bot dip-buy lama)
-----------------------------------------------
Satu posisi long CBBTC/USDC, 30% kas per entry, maksimal 2 trip dalam
jendela 1440 bar (1 menit). Entry hanya saat RSI(14) Wilder kembali
menembus ke atas 35 setelah sempat di bawah 35 ("RSI reclaim"):
pantulan yang sudah dikonfirmasi oleh momentum, bukan sekadar harga
turun dari tertinggi.

Kenapa bukan dip-buy: bot dip-buy lama selalu memakai 100% kas, jadi
satu trip yang kena stop-loss saja sudah -$4,60..-$6,60 dan aturan
ketat out-of-sample (worst >= -$3) mustahil dipenuhi. Bot ini memakai
30% kas per trip + anggaran kerugian (tidak ada entry baru bila
realized PnL sudah <= -$2,00) sehingga satu trip yang gagal tidak
pernah menghancurkan satu window.

Exit satu posisi, yang mana dulu tercapai (diukur dari open bar saat
buy terisi, bukan dari cost basis, supaya levelnya sama dengan yang
dipakai saat screening):
* take-profit +60 bps di atas entry open,
* stop-loss -20 bps di bawah entry open,
* max_hold 60 bar.

Protokol
--------
Berbicara agent-fun/bars-replay/v1 lewat shim vendor: shim membaca
NDJSON dari stdin — pertama pesan hello, lalu satu batch per menit,
lalu done — dan memanggil on_batch(state, batch); balasan berupa
list orders (boleh kosong). Satu batch membawa bar yang baru tutup,
fills dari orders batch sebelumnya, dan akun. Order yang diputuskan
pada batch menit t terisi pada open bar berikutnya.

Determinisme
------------
Penuh: tanpa jam dinding, tanpa random, tanpa environment, tanpa file.
Semua state berasal dari bar, fills, dan state yang dikirim harness.
Dua eksekusi pada data yang sama menghasilkan orders yang sama
persis. Hanya standard library yang dipakai.
"""

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.join(_HERE, "vendor"))

from params import P

SYMBOL = "CBBTC"
BPS = 10_000
WINDOW_BARS = 1440  # jendela race: 24 jam x 60 bar/menit


def rsi(closes, period=14):
    """Wilder RSI, integer math, None bila data belum cukup."""
    if len(closes) < period + 1:
        return None
    gain = 0
    loss = 0
    for i in range(1, period + 1):
        d = closes[i] - closes[i - 1]
        if d > 0:
            gain += d
        else:
            loss -= d
    avg_gain = gain // period
    avg_loss = loss // period
    for i in range(period + 1, len(closes)):
        d = closes[i] - closes[i - 1]
        if d > 0:
            avg_gain = (avg_gain * (period - 1) + d) // period
            avg_loss = (avg_loss * (period - 1)) // period
        else:
            avg_gain = (avg_gain * (period - 1)) // period
            avg_loss = (avg_loss * (period - 1) - d) // period
    if avg_loss == 0:
        return 100
    return 100 - (100 * avg_loss) // (avg_gain + avg_loss)


class Bot:
    def __init__(self):
        self.closes = []
        self.entry_seq = None      # seq saat posisi pertama terlihat
        self.entry_open = None     # open bar saat buy terisi
        self.buy_cash = None       # kas sebelum buy (untuk realized PnL)
        self.pending_buy_cash = None
        self.trips = 0             # jumlah buy fill
        self.realized = 0          # realized PnL kumulatif, quote units
        self.orders = []

    def on_batch(self, state, batch):
        self.orders = []
        if state.warming_up:
            return []
        bar = state.latest.get(SYMBOL)
        if bar is None:
            return []
        self.closes.append(int(bar["c"]))
        held = state.positions.get(SYMBOL)
        close = int(bar["c"])

        if held is None:
            # Posisi baru saja tertutup (sell fill masuk di batch ini):
            # realized = kas sekarang - kas sebelum buy trip ini.
            if self.entry_seq is not None:
                self.realized += state.cash - self.buy_cash
                self.entry_seq = None
                self.entry_open = None
                self.buy_cash = None
            # --- entry ---
            if len(self.closes) >= 16 and self.trips < P["max_trips"]:
                if state.seq >= WINDOW_BARS - P["no_entry_last"]:
                    return []
                if self.realized <= -P["loss_budget"]:
                    return []
                r_now = rsi(self.closes)
                r_prev = rsi(self.closes[:-1])
                if r_now is None or r_prev is None:
                    return []
                if r_prev < P["rsi_level"] <= r_now:
                    amount = min(
                        state.cash * P["size_frac_num"] // P["size_frac_den"],
                        state.weight_room(SYMBOL),
                    )
                    if amount >= int(state.hello["fees"]["min_notional_quote_units"]):
                        self.pending_buy_cash = state.cash
                        self.orders.append(
                            {
                                "side": "buy",
                                "symbol": SYMBOL,
                                "notional_quote_units": amount,
                                "max_slippage_bps": P["max_slippage_bps"],
                            }
                        )
            return self.orders

        # --- posisi terbuka ---
        if self.entry_seq is None:
            # Buy fill baru masuk di batch ini: catat entry dari bar ini
            # (fill terjadi di open bar ini, persis seperti screening).
            self.entry_seq = state.seq
            self.entry_open = int(bar["o"])
            self.buy_cash = self.pending_buy_cash
            self.trips += 1
            return []

        held_value = state.value(SYMBOL, held.qty)
        bars_held = state.seq - self.entry_seq
        tp_hit = close * BPS >= self.entry_open * (BPS + P["tp_bps"])
        sl_hit = close * BPS <= self.entry_open * (BPS - P["sl_bps"])
        if tp_hit or sl_hit or bars_held >= P["max_hold"]:
            self.orders.append(
                {
                    "side": "sell",
                    "symbol": SYMBOL,
                    "qty": held.qty,
                    "max_slippage_bps": P["max_slippage_bps"],
                }
            )
        return self.orders


def main():
    from vendor.makefun_bars import run

    bot = Bot()
    run(bot.on_batch)


if __name__ == "__main__":
    main()
