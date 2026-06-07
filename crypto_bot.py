#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================
CryptoPriceBot v2.1 — Real-time Cryptocurrency Technical Analysis
   加密货币实时监控与技术分析工具
=============================================================
Category:   CLI Tool
License:    MIT
Donate:     0xAfe9B67B1DF618FAeD32dC71E3458cf549f26697 (ETH/USDT)
=============================================================
Binance-powered crypto price monitor with SMA, EMA, RSI,
MACD indicators and auto-generated trading signals.
=============================================================
"""
import argparse
import json
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

sys.stdout.reconfigure(encoding="utf-8")

__version__ = "2.1.0"
__wallet__  = "0xAfe9B67B1DF618FAeD32dC71E3458cf549f26697"

# ─── Public API ─────────────────────────────────────────────

class CryptoBot:
    """
    Cryptocurrency technical analysis bot.

    Usage::

        bot = CryptoBot(proxy="http://127.0.0.1:10793")
        result = bot.analyze("BTCUSDT", interval="4h")
        print(f"Price: ${result['price']:,.2f}, RSI: {result['rsi']}")

    Parameters:
        proxy: Optional HTTP proxy URL (e.g. ``"http://127.0.0.1:10793"``).
    """

    # Valid Binance kline intervals
    INTERVALS = ("1m", "3m", "5m", "15m", "30m",
                 "1h", "2h", "4h", "6h", "8h", "12h",
                 "1d", "3d", "1w", "1M")

    def __init__(self, proxy: Optional[str] = None) -> None:
        self._base = "https://api.binance.com"
        self._session = requests.Session()
        
        # Retry strategy
        retry = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry)
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)
        
        # Proxy
        if proxy:
            self._session.proxies = {"http": proxy, "https": proxy}
        
        self._session.headers.update({"User-Agent": "CryptoPriceBot/2.1"})

    # ── HTTP helpers ───────────────────────────────────

    def _fetch(self, url: str) -> Any:
        """Fetch JSON from Binance API."""
        resp = self._session.get(url, timeout=15)
        resp.raise_for_status()
        return resp.json()

    # ── Data methods ───────────────────────────────────

    def get_price(self, symbol: str = "BTCUSDT") -> float:
        """Return the latest price for *symbol*."""
        data = self._fetch(f"{self._base}/api/v3/ticker/price?symbol={symbol.upper()}")
        return float(data["price"])

    def get_24hr(self, symbol: str = "BTCUSDT") -> Dict[str, float]:
        """Return 24-hour ticker statistics for *symbol*."""
        data = self._fetch(f"{self._base}/api/v3/ticker/24hr?symbol={symbol.upper()}")
        return {
            "price":       float(data["lastPrice"]),
            "change":      float(data["priceChange"]),
            "change_pct":  float(data["priceChangePercent"]),
            "high":        float(data["highPrice"]),
            "low":         float(data["lowPrice"]),
            "volume":      float(data["volume"]),
        }

    def get_klines(self, symbol: str = "BTCUSDT",
                   interval: str = "1h", limit: int = 100) -> List[List]:
        """Fetch kline (candlestick) data from Binance."""
        url = (f"{self._base}/api/v3/klines"
               f"?symbol={symbol.upper()}&interval={interval}&limit={limit}")
        return self._fetch(url)

    # ── Technical Indicators ───────────────────────────

    @staticmethod
    def sma(data: List[float], period: int) -> Optional[float]:
        """Simple Moving Average."""
        if len(data) < period:
            return None
        return sum(data[-period:]) / period

    @staticmethod
    def ema(data: List[float], period: int) -> Optional[float]:
        """Exponential Moving Average."""
        if len(data) < period:
            return None
        multiplier = 2 / (period + 1)
        ema_val = sum(data[:period]) / period
        for price in data[period:]:
            ema_val = (price - ema_val) * multiplier + ema_val
        return ema_val

    @staticmethod
    def rsi(data: List[float], period: int = 14) -> Optional[float]:
        """Relative Strength Index."""
        if len(data) < period + 1:
            return None
        gains = losses = 0.0
        for i in range(-period, 0):
            delta = data[i] - data[i - 1]
            if delta > 0:
                gains += delta
            else:
                losses -= delta
        avg_gain = gains / period
        avg_loss = losses / period
        if avg_loss == 0:
            return 100.0
        return 100 - 100 / (1 + avg_gain / avg_loss)

    @staticmethod
    def macd(data: List[float]) -> tuple:
        """Return (MACD_line, signal_line)."""
        ema12 = CryptoBot.ema(data, 12)
        ema26 = CryptoBot.ema(data, 26)
        if ema12 is None or ema26 is None:
            return None, None
        return ema12 - ema26, None  # signal requires more data points

    # ── Analysis ───────────────────────────────────────

    def analyze(self, symbol: str = "BTCUSDT",
                interval: str = "1h") -> Dict:
        """
        Run full technical analysis on *symbol*.

        Returns:
            A dict with keys: symbol, price, interval, sma20, sma50,
            ema12, ema26, rsi, macd, signals, time.
        """
        klines = self.get_klines(symbol, interval)
        closes = [float(k[4]) for k in klines]
        price = closes[-1]

        sma20_val = self.sma(closes, 20)
        sma50_val = self.sma(closes, 50)
        ema12_val = self.ema(closes, 12)
        ema26_val = self.ema(closes, 26)
        rsi_val   = self.rsi(closes)
        macd_val, _ = self.macd(closes)

        # Generate signals
        signals: List[str] = []
        if sma20_val and sma50_val:
            signals.append("BULLISH" if sma20_val > sma50_val else "BEARISH")
        if rsi_val is not None:
            if rsi_val > 70:
                signals.append("OVERBOUGHT")
            elif rsi_val < 30:
                signals.append("OVERSOLD")
        if macd_val is not None:
            signals.append("MACD_UP" if macd_val > 0 else "MACD_DOWN")

        return {
            "symbol":   symbol.upper(),
            "price":    round(price, 2),
            "interval": interval,
            "sma20":    round(sma20_val, 2) if sma20_val else None,
            "sma50":    round(sma50_val, 2) if sma50_val else None,
            "ema12":    round(ema12_val, 2) if ema12_val else None,
            "ema26":    round(ema26_val, 2) if ema26_val else None,
            "rsi":      round(rsi_val, 1) if rsi_val is not None else None,
            "macd":     round(macd_val, 4) if macd_val is not None else None,
            "signals":  signals,
            "time":     datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    def monitor(self, symbols: Optional[List[str]] = None,
                interval: str = "1h") -> Dict[str, Dict]:
        """
        Analyze multiple symbols.

        Args:
            symbols: List of trading pairs (default: BTC, ETH, BNB).
            interval: Kline interval.

        Returns:
            ``{symbol: analysis_dict, ...}``
        """
        symbols = symbols or ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
        results: Dict[str, Dict] = {}
        for sym in symbols:
            try:
                results[sym] = self.analyze(sym, interval)
            except Exception as exc:
                results[sym] = {"error": str(exc)}
        return results


    # ── Bollinger Bands ────────────────────────────
    @staticmethod
    def bollinger_bands(data: List[float], period: int = 20, std_dev: int = 2):
        """Return (upper_band, middle_band, lower_band)."""
        if len(data) < period:
            return None, None, None
        sma_val = CryptoBot.sma(data, period)
        recent = data[-period:]
        mean = sum(recent) / period
        variance = sum((x - mean) ** 2 for x in recent) / period
        stdev = variance ** 0.5
        return (
            round(sma_val + std_dev * stdev, 2),
            round(sma_val, 2),
            round(sma_val - std_dev * stdev, 2),
        )

    # ── ATR (Average True Range) ────────────────────
    @staticmethod
    def atr_from_klines(klines: List[List], period: int = 14) -> Optional[float]:
        """Calculate ATR from kline data (each row: [time, open, high, low, close, ...])."""
        if len(klines) < period + 1:
            return None
        trs = []
        for i in range(1, len(klines)):
            h, l, prev_c = float(klines[i][2]), float(klines[i][3]), float(klines[i - 1][4])
            tr = max(h - l, abs(h - prev_c), abs(l - prev_c))
            trs.append(tr)
        return round(sum(trs[-period:]) / period, 4)

    # ── Backtesting Engine ──────────────────────────
    def backtest(self, symbol: str = "BTCUSDT", interval: str = "1h",
                 strategy: str = "sma_cross", capital: float = 10000,
                 lookback_days: int = 90) -> Dict:
        """
        Backtest a trading strategy on historical data.

        Strategies:
          - "sma_cross": Buy when SMA20 crosses above SMA50, sell when crosses below.
          - "rsi_extreme": Buy when RSI < 30 (oversold), sell when RSI > 70 (overbought).
          - "macd_signal": Buy when MACD turns positive, sell when negative.

        Returns dict with total_return, win_rate, max_drawdown, trades, final_capital.
        """
        # Fetch enough candles (capped to avoid memory issues)
        limit = min(500, max(100, lookback_days * 2))
        klines = self.get_klines(symbol, interval, limit=limit)
        closes = [float(k[4]) for k in klines]

        trades = []
        position = None  # None = flat, 'long'
        entry_price = 0.0
        cash = capital
        equity_curve = [capital]

        for i in range(51, len(closes)):  # need 50 candles for SMA50
            window = closes[:i + 1]
            price = closes[i]

            # Compute indicators
            sma20 = self.sma(window, 20)
            sma50 = self.sma(window, 50)
            rsi_val = self.rsi(window)
            ema12 = self.ema(window, 12)
            ema26 = self.ema(window, 26)

            signal = None  # 'buy', 'sell', or None

            if strategy == "sma_cross":
                if sma20 and sma50:
                    prev20 = self.sma(closes[:i], 20)
                    prev50 = self.sma(closes[:i], 50)
                    if prev20 and prev50:
                        if prev20 <= prev50 and sma20 > sma50:
                            signal = 'buy'
                        elif prev20 >= prev50 and sma20 < sma50:
                            signal = 'sell'

            elif strategy == "rsi_extreme":
                if rsi_val:
                    if rsi_val < 30:
                        signal = 'buy'
                    elif rsi_val > 70:
                        signal = 'sell'

            elif strategy == "macd_signal":
                if ema12 and ema26:
                    prev_macd = self.ema(closes[:i], 12) - self.ema(closes[:i], 26)
                    cur_macd = ema12 - ema26
                    if prev_macd and cur_macd:
                        if prev_macd <= 0 and cur_macd > 0:
                            signal = 'buy'
                        elif prev_macd >= 0 and cur_macd < 0:
                            signal = 'sell'

            # Execute trades
            if signal == 'buy' and position is None:
                entry_price = price
                position = 'long'
            elif signal == 'sell' and position == 'long':
                pnl = (price - entry_price) / entry_price
                trades.append({
                    'entry': round(entry_price, 2),
                    'exit': round(price, 2),
                    'pnl_pct': round(pnl * 100, 2),
                    'bars_held': i - next(j for j, t in enumerate(trades[::-1]) if True) if trades else i,
                })
                cash *= (1 + pnl)
                position = None

            # Track equity
            if position == 'long':
                equity = cash * (price / entry_price)
            else:
                equity = cash
            equity_curve.append(equity)

        # Close remaining position at last price
        if position == 'long':
            pnl = (closes[-1] - entry_price) / entry_price
            trades.append({'entry': round(entry_price, 2), 'exit': round(closes[-1], 2), 'pnl_pct': round(pnl * 100, 2)})
            cash *= (1 + pnl)

        # Calculate stats
        wins = [t for t in trades if t['pnl_pct'] > 0]
        win_rate = len(wins) / len(trades) * 100 if trades else 0
        total_return = (cash - capital) / capital * 100

        # Max drawdown
        peak = equity_curve[0]
        max_dd = 0.0
        for eq in equity_curve:
            if eq > peak:
                peak = eq
            dd = (peak - eq) / peak * 100
            if dd > max_dd:
                max_dd = dd

        return {
            "symbol": symbol.upper(),
            "strategy": strategy,
            "interval": interval,
            "initial_capital": capital,
            "final_capital": round(cash, 2),
            "total_return_pct": round(total_return, 2),
            "total_trades": len(trades),
            "win_rate_pct": round(win_rate, 1),
            "max_drawdown_pct": round(max_dd, 2),
            "trades": trades[-10:],  # last 10 trades
        }


# ─── CLI Interface (参考 yt-dlp 风格) ──────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="crypto_bot",
        description=f"CryptoPriceBot v{__version__} — Cryptocurrency technical analysis CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  crypto_bot.py                           # Analyze BTC, ETH, BNB (default)
  crypto_bot.py --symbol SOLUSDT          # Single symbol
  crypto_bot.py -s BTCUSDT -s ETHUSDT     # Multiple symbols
  crypto_bot.py --interval 4h             # 4-hour candles
  crypto_bot.py --24hr                    # Show 24hr stats
  crypto_bot.py --proxy http://127.0.0.1:10793  # Via proxy
  crypto_bot.py --backtest BTCUSDT        # Backtest strategies
  crypto_bot.py --backtest ETHUSDT --strategy rsi_extreme
  crypto_bot.py --list-intervals          # List all intervals
        """
    )
    p.add_argument("-s", "--symbol", action="append", dest="symbols",
                   help="Trading pair (repeatable, default: BTCUSDT ETHUSDT BNBUSDT)")
    p.add_argument("-i", "--interval", default="1h",
                   help="Kline interval (default: 1h)")
    p.add_argument("--24hr", action="store_true", dest="show_24hr",
                   help="Show 24-hour ticker statistics")
    p.add_argument("-p", "--proxy",
                   help="HTTP proxy URL")
    p.add_argument("-j", "--json", action="store_true",
                   help="Output as JSON")
    p.add_argument("--backtest", metavar="SYMBOL",
                   help="Run strategy backtest on SYMBOL")
    p.add_argument("--strategy", default="sma_cross",
                   choices=["sma_cross", "rsi_extreme", "macd_signal"],
                   help="Backtest strategy (default: sma_cross)")
    p.add_argument("--capital", type=float, default=10000,
                   help="Initial capital for backtest (default: 10000)")
    p.add_argument("--list-intervals", action="store_true",
                   help="List valid kline intervals and exit")
    p.add_argument("--version", action="version",
                   version=f"%(prog)s {__version__}")
    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.list_intervals:
        print("Valid intervals:", ", ".join(CryptoBot.INTERVALS))
        return

    bot = CryptoBot(proxy=args.proxy)

    if args.backtest:
        bt = bot.backtest(args.backtest, interval=args.interval,
                         strategy=args.strategy, capital=args.capital)
        print(f"""
  CryptoPriceBot Backtest Report
  {'─' * 50}
  Symbol:          {bt['symbol']}
  Strategy:        {bt['strategy']}
  Interval:        {bt['interval']}
  Initial Capital: {bt['initial_capital']:,.2f}
  Final Capital:   {bt['final_capital']:,.2f}
  Total Return:    {bt['total_return_pct']:+.2f}%
  Total Trades:    {bt['total_trades']}
  Win Rate:        {bt['win_rate_pct']:.1f}%
  Max Drawdown:    -{bt['max_drawdown_pct']:.2f}%
  {'─' * 50}
  Recent Trades (last 10):""")
        for t in bt['trades']:
            icon = '✅' if t['pnl_pct'] > 0 else '❌'
            print(f"    {icon} Entry: {t['entry']:>10,.2f}  Exit: {t['exit']:>10,.2f}  PnL: {t['pnl_pct']:>+7.2f}%")
        print(f"  {'─' * 50}\n")
        return

    symbols = args.symbols or ["BTCUSDT", "ETHUSDT", "BNBUSDT"]

    if args.json:
        results = bot.monitor(symbols, args.interval)
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    print(f"\n  CryptoPriceBot v{__version__}")
    print(f"  {'─' * 55}")
    print(f"  {'Symbol':<10} {'Price':>14} {'RSI':>6} {'24h%':>7}  Signals")
    print(f"  {'─' * 55}")

    for sym in symbols:
        try:
            analysis = bot.analyze(sym, args.interval)

            if args.show_24hr:
                stats = bot.get_24hr(sym)
                chg = f"{stats['change_pct']:+.1f}%"
            else:
                chg = "──"

            sig = ", ".join(analysis["signals"]) if analysis["signals"] else "─"
            rsi_display = f"{analysis['rsi']:.0f}" if analysis["rsi"] is not None else "─"
            print(f"  {sym:<10} ${analysis['price']:>13,.2f} {rsi_display:>5}  {chg:>6}  {sig}")

        except Exception as exc:
            print(f"  {sym:<10} Error: {exc}")

    print(f"  {'─' * 55}")
    print(f"  Interval: {args.interval}  |  Time: {datetime.now().strftime('%H:%M:%S')}")
    print(f"  Donate: {__wallet__} (USDT/ERC20)\n")


if __name__ == "__main__":
    main()
