# Crypto Price Bot ₿

> 加密货币实时价格监控 + 技术分析工具

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ 功能特性

- ✅ **实时价格** - BTC/ETH/BNB等主流币种
- ✅ **技术指标** - SMA / EMA / RSI / MACD 全支持
- ✅ **买卖信号** - 自动生成交易建议
- ✅ **多时间周期** - 1h/4h/1d 任意切换
- ✅ **轻量级** - 纯Python，无外部依赖

## 🚀 快速开始

```bash
pip install requests
```

```python
from crypto_bot import CryptoBot

bot = CryptoBot()

# BTC分析
result = bot.analyze("BTCUSDT")
print(f"价格: ${result['price']:,.2f}")
print(f"RSI: {result['rsi']}")
print(f"信号: {', '.join(result['signals']) if result['signals'] else '无信号'}")

# ETH分析
result = bot.analyze("ETHUSDT")
```

## 📊 输出示例

```
BTCUSDT    $70,234.50  RSI: 54.2 | 买入
ETHUSDT    $3,521.80   RSI: 48.7 | 卖出
BNBUSDT    $612.30     RSI: 62.1 | 超买
```

## 💎 支持项目

如果这个工具帮到了你，欢迎打赏支持持续开发！

**USDT (ERC20):** `0xAfe9B67B1DF618FAeD32dC71E3458cf549f26697`

---

*Made with ❤️ by [K2st0r](https://github.com/K2st0r)*
