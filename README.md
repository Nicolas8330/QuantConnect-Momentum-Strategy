# QuantConnect Momentum Strategy

This repository contains a Python-based momentum trading algorithm designed for the QuantConnect platform. The strategy trades the SPXL ETF using a combination of moving averages for signal generation and volatility-based risk management to mitigate market risks.

## Overview

The algorithm tracks SPXL daily price data and calculates short- and long-term moving averages to generate buy and sell signals. A volatility threshold is implemented to liquidate positions during periods of excessive market fluctuations. The strategy also includes visualizations for price evolution, volatility bands, and trading signals, providing a clear understanding of its performance.

## How to Use

1. Copy the code into your QuantConnect Python project.
2. Run backtests on the QuantConnect platform to evaluate its performance.
3. Adjust parameters like the volatility threshold to fine-tune the strategy for specific market conditions.

## Requirements

- QuantConnect Python Algorithm environment.
- Financial data access for SPXL (provided by QuantConnect).

## Disclaimer

This project is for educational purposes only and should not be considered financial advice. Always perform your own due diligence before deploying any trading strategy.
