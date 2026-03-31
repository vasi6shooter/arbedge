<div align="center">

# ⚡ ArbEdge

### Real-Time Sports Arbitrage Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Plotly](https://img.shields.io/badge/Plotly-Interactive_Charts-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com)
[![License](https://img.shields.io/badge/License-MIT-00d4aa?style=for-the-badge)](LICENSE)

*A full-stack data engineering project that scans live betting odds from Ontario-licensed sportsbooks, detects arbitrage opportunities using probability theory, and presents actionable insights through a professional trading-style dashboard.*

</div>

---

## 📌 The Problem

Sportsbooks independently set their own odds for sporting events. Occasionally, the odds across different bookmakers **disagree enough** that a bettor can place bets on **all possible outcomes** across different platforms and **guarantee a profit** regardless of the result. These windows last **seconds to minutes** before the market corrects itself.

Manually checking odds across 5+ sportsbooks for hundreds of events is impossible. **ArbEdge automates this entirely.**

## 💡 The Solution

ArbEdge is an end-to-end data pipeline that:

1. **Ingests** live odds data from The Odds API across 10 sports and 3 market types
2. **Filters** to only Ontario-licensed sportsbooks (bet365, DraftKings, BetMGM, Betway, FanDuel)
3. **Analyzes** every market opportunity using implied probability mathematics
4. **Detects** arbitrage where total implied probability drops below 100%
5. **Calculates** optimal stake distribution to maximize guaranteed profit
6. **Visualizes** everything in a real-time interactive dashboard

## 🧮 How Arbitrage Works

An arbitrage opportunity exists when the sum of implied probabilities across different bookmakers falls below 1.0.

