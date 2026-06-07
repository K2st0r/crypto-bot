<div align="center">

# CryptoPriceBot

**Real-time Cryptocurrency Technical Analysis CLI**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-2.1.0-purple.svg)](https://github.com/K2st0r/crypto-bot/releases)
[![Donate](https://img.shields.io/badge/Donate-USDT-red.svg)](#donate)

</div>

---

## Table of Contents

- [English](#english)
  - [What is CryptoPriceBot?](#what-is-cryptopricebot)
  - [Features](#features)
  - [Installation](#installation)
  - [CLI Usage](#cli-usage)
  - [Python API](#python-api)
  - [Technical Indicators](#technical-indicators)
- [中文](#chinese)
- [Donate / 打赏](#donate--打赏)

---

## English

### What is CryptoPriceBot?

CryptoPriceBot is a **command-line tool and Python library** for real-time cryptocurrency price monitoring and technical analysis. It fetches live market data from **Binance API** and computes SMA, EMA, RSI, and MACD indicators — then generates human-readable trading signals.

No paid APIs. No complex setup. Just `python crypto_bot.py`.

### Features

| Category | Description |
|----------|-------------|
| **Real-time prices** | BTC, ETH, BNB, SOL, XRP, DOGE — any Binance USDT pair |
| **24h market stats** | Price change, percentage, high/low, volume |
| **Technical indicators** | SMA (20/50), EMA (12/26), RSI (14), MACD |
| **Trading signals** | BULLISH / BEARISH / OVERBOUGHT / OVERSOLD / MACD direction |
| **Multi-symbol** | Monitor multiple trading pairs in one command |
| **JSON output** | Machine-readable `--json` flag |
| **Proxy support** | HTTP proxy for users in restricted networks |
| **Zero dependencies** | Pure Python standard library — no `pip install` needed |

### Installation

```bash
git clone https://github.com/K2st0r/crypto-bot.git
cd crypto-bot
# That's it — no dependencies required!
```

### CLI Usage

```bash
# Default: analyze BTC, ETH, BNB (1h candles)
python crypto_bot.py

# Analyze a single symbol
python crypto_bot.py --symbol SOLUSDT

# Multiple symbols
python crypto_bot.py -s BTCUSDT -s ETHUSDT -s DOGEUSDT

# 4-hour candles
python crypto_bot.py --interval 4h

# Show 24-hour market stats alongside analysis
python crypto_bot.py --24hr

# Via HTTP proxy (Chinese mainland users need this)
python crypto_bot.py --proxy http://127.0.0.1:10793

# Machine-readable JSON output
python crypto_bot.py --json > analysis.json

# List all valid intervals
python crypto_bot.py --list-intervals
```

**Output example:**

```
  CryptoPriceBot v2.1.0
  ───────────────────────────────────────────────────────
  Symbol          Price    RSI   24h%    Signals
  ───────────────────────────────────────────────────────
  BTCUSDT     $68,421.50     58   +1.2%   BULLISH, MACD_UP
  ETHUSDT      $3,892.30     62   +0.8%   BULLISH
  BNBUSDT        $612.40     41   -2.1%   BEARISH, OVERSOLD
  ───────────────────────────────────────────────────────
  Interval: 1h  |  Time: 16:00:00
```

### Python API

```python
from crypto_bot import CryptoBot

# Initialize (proxy optional)
bot = CryptoBot(proxy="http://127.0.0.1:10793")

# Current price
price = bot.get_price("BTCUSDT")        # -> 68421.50

# 24h stats
stats = bot.get_24hr("ETHUSDT")
# -> {"price": 3892.30, "change_pct": 0.8, "high": 3920.0, "volume": 123456789}

# Full technical analysis
analysis = bot.analyze("BTCUSDT", interval="4h")
# -> {"symbol":"BTCUSDT","price":68421.5,"rsi":58.3,"signals":["BULLISH","MACD_UP"],...}

# Monitor multiple symbols
results = bot.monitor(["BTCUSDT", "SOLUSDT", "DOGEUSDT"])
```

### Technical Indicators

| Indicator | Parameters | What it tells you |
|-----------|-----------|-------------------|
| SMA (Simple Moving Average) | 20, 50 periods | Trend direction — SMA20 > SMA50 = bullish |
| EMA (Exponential Moving Average) | 12, 26 periods | Like SMA but weights recent prices more |
| RSI (Relative Strength Index) | 14 periods | Momentum — >70 overbought, <30 oversold |
| MACD | 12/26/9 | Trend strength — >0 bullish, <0 bearish |
| **Bollinger Bands** | 20 periods, 2σ | Volatility — price near upper=overbought, near lower=oversold |
| **ATR** | 14 periods | Market volatility measurement |

### Backtesting (New in v2.3)

Test trading strategies on historical data before risking real money:

```bash
# SMA crossover strategy (default)
python crypto_bot.py --backtest BTCUSDT --interval 1d --capital 10000

# RSI extreme strategy
python crypto_bot.py --backtest ETHUSDT --strategy rsi_extreme

# MACD signal strategy
python crypto_bot.py --backtest SOLUSDT --strategy macd_signal --capital 5000
```

**Output:**
```
  CryptoPriceBot Backtest Report
  ──────────────────────────────────────────────────
  Symbol:          BTCUSDT
  Strategy:        sma_cross
  Initial Capital: $10,000.00
  Final Capital:   $12,450.32
  Total Return:    +24.50%
  Total Trades:    15
  Win Rate:        60.0%
  Max Drawdown:    -8.32%
  ──────────────────────────────────────────────────
  Recent Trades:
    ✅ Entry: $42,150.00  Exit: $43,800.00  PnL:  +3.92%
    ❌ Entry: $43,800.00  Exit: $42,500.00  PnL:  -2.97%
```

**Available Strategies:**
- `sma_cross` — Buy when SMA20 crosses above SMA50
- `rsi_extreme` — Buy at RSI<30, sell at RSI>70
- `macd_signal` — Buy when MACD turns positive

---

## 中文

### 概述

CryptoPriceBot 是一个**命令行工具 + Python 库**，用于加密货币实时价格监控和技术分析。数据来自 **Binance API**（免费），支持 SMA、EMA、RSI、MACD 等主流指标。

### 快速开始

```bash
git clone https://github.com/K2st0r/crypto-bot.git
cd crypto-bot
# 无需安装任何依赖！
python crypto_bot.py
```

### CLI 命令

```bash
python crypto_bot.py                     # 默认分析 BTC/ETH/BNB
python crypto_bot.py -s SOLUSDT          # 单个币种
python crypto_bot.py -s BTC -s ETH -s DOGE  # 多个币种
python crypto_bot.py --interval 4h       # 4小时K线
python crypto_bot.py --24hr              # 显示24小时行情
python crypto_bot.py --proxy http://127.0.0.1:10793  # 通过代理
python crypto_bot.py --json              # JSON 格式输出
```

### Python API 示例

```python
from crypto_bot import CryptoBot
bot = CryptoBot(proxy="http://127.0.0.1:10793")

# 实时分析
r = bot.analyze("BTCUSDT", interval="1h")
print(f"价格: ${r['price']:,.2f}, RSI: {r['rsi']}, 信号: {', '.join(r['signals'])}")

# 策略回测
bt = bot.backtest("BTCUSDT", interval="1d", strategy="sma_cross", capital=10000)
print(f"收益率: {bt['total_return_pct']:+.2f}%, 胜率: {bt['win_rate_pct']:.1f}%")
```

### 支持的交易对

任意 Binance USDT 交易对：`BTCUSDT`, `ETHUSDT`, `BNBUSDT`, `SOLUSDT`, `XRPUSDT`, `DOGEUSDT`, `ADAUSDT`, `AVAXUSDT`, `DOTUSDT`, `LINKUSDT` ...

### 支持的K线周期

`1m`, `3m`, `5m`, `15m`, `30m`, `1h`, `2h`, `4h`, `6h`, `8h`, `12h`, `1d`, `3d`, `1w`, `1M`

---

## Donate / 打赏

<div align="center">
<img src="https://raw.githubusercontent.com/K2st0r/crypto-bot/main/static/zan.png" width="200" alt="WeChat Pay">

📱 微信扫码赞赏

**USDT (ERC20):** `0xAfe9B67B1DF618FAeD32dC71E3458cf549f26697`

</div>

---

MIT License · Made with ❤️ by [K2st0r](https://github.com/K2st0r)
