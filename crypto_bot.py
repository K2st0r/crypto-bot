#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CryptoPriceBot Pro v1.0 - 加密货币价格监控+技术分析
==============================================
功能: 实时价格、EMA/RSI/MACD分析、买卖信号、多币种
价格: 50 USDT
购买: 0xAfe9B67B1DF618FAeD32dC71E3458cf549f26697 (ETH/USDT)
==============================================
"""
import json, time, urllib.request, urllib.error
from datetime import datetime

__version__ = "1.0.0" 
__price__ = "50 USDT"
__wallet__ = "0xAfe9B67B1DF618FAeD32dC71E3458cf549f26697"

class CryptoBot:
    """加密货币技术分析机器人"""
    
    def __init__(self, proxy=None):
        self.base = "https://api.binance.com"
        self.opener = None
        if proxy:
            proxy_h = urllib.request.ProxyHandler({'http': proxy, 'https': proxy})
            self.opener = urllib.request.build_opener(proxy_h)
    
    def _fetch(self, url):
        h = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url, headers=h)
        opener = self.opener or urllib.request.build_opener()
        resp = opener.open(req, timeout=15)
        return json.loads(resp.read())
    
    def get_price(self, symbol="BTCUSDT"):
        """获取当前价格"""
        data = self._fetch(f"{self.base}/api/v3/ticker/price?symbol={symbol}")
        return float(data["price"])
    
    def get_klines(self, symbol="BTCUSDT", interval="1h", limit=100):
        """获取K线数据"""
        return self._fetch(f"{self.base}/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}")
    
    def sma(self, data, period):
        if len(data) < period:
            return None
        return sum(data[-period:]) / period
    
    def ema(self, data, period):
        if len(data) < period:
            return None
        m = 2 / (period + 1)
        ema = sum(data[:period]) / period
        for p in data[period:]:
            ema = (p - ema) * m + ema
        return ema
    
    def rsi(self, data, period=14):
        if len(data) < period + 1:
            return None
        gains, losses = 0, 0
        for i in range(-period, 0):
            d = data[i] - data[i-1]
            if d > 0: gains += d
            else: losses -= d
        ag, al = gains/period, losses/period
        return 100 - 100/(1 + ag/al) if al else 100
    
    def macd(self, data):
        e12 = self.ema(data, 12)
        e26 = self.ema(data, 26)
        if e12 is None or e26 is None:
            return None, None
        return e12 - e26, self.ema([e12 - e26], 9) if len(data) > 26 else None
    
    def analyze(self, symbol="BTCUSDT", interval="1h"):
        """完整技术分析"""
        klines = self.get_klines(symbol, interval)
        closes = [float(k[4]) for k in klines]
        price = closes[-1]
        
        sma20 = self.sma(closes, 20)
        sma50 = self.sma(closes, 50)
        ema12 = self.ema(closes, 12)
        ema26 = self.ema(closes, 26)
        rsi_val = self.rsi(closes)
        macd_line, signal = self.macd(closes)
        
        signals = []
        if sma20 and sma50:
            signals.append("买入" if sma20 > sma50 else "卖出")
        if rsi_val:
            if rsi_val > 70: signals.append("超买")
            elif rsi_val < 30: signals.append("超卖")
        if macd_line and signal:
            signals.append("MACD金叉" if macd_line > signal else "MACD死叉")
        
        return {
            "symbol": symbol, "price": price,
            "sma20": round(sma20, 2) if sma20 else None,
            "sma50": round(sma50, 2) if sma50 else None,
            "rsi": round(rsi_val, 1) if rsi_val else None,
            "macd": round(macd_line, 2) if macd_line else None,
            "signal": round(signal, 2) if signal else None,
            "signals": signals,
            "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }


if __name__ == "__main__":
    bot = CryptoBot()
    print(f"\nCryptoPriceBot Pro v{__version__}")
    print(f"Price: {__price__}")
    print(f"Wallet: {__wallet__}")
    print()
    
    for sym in ["BTCUSDT", "ETHUSDT", "BNBUSDT"]:
        try:
            r = bot.analyze(sym)
            sig_str = ", ".join(r["signals"]) if r["signals"] else "无信号"
            print(f"  {sym:<10} ${r['price']:<12,.2f} RSI:{r['rsi']} | {sig_str}")
        except Exception as e:
            print(f"  {sym:<10} Error: {e}")
