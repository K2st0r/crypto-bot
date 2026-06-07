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
