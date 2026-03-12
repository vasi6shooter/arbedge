# ⚡ ArbEdge — Sports Arbitrage Intelligence Dashboard

Real-time sports arbitrage scanner built for Ontario-licensed sportsbooks.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)
![License](https://img.shields.io/badge/License-MIT-green)

## What It Does

ArbEdge scans live betting odds from multiple Ontario sportsbooks
(bet365, DraftKings, BetMGM, Betway, FanDuel) and automatically
detects **arbitrage opportunities** — situations where you can bet
on all outcomes across different bookmakers and guarantee a profit
regardless of the result.

## Features

- **Real-time odds scanning** across 10+ sports (Soccer, NBA, NHL, UFC)
- **Multi-market analysis** — h2h, spreads, and totals
- **Arb Radar gauge** — shows how close the market is to arb territory
- **Interactive profit simulator** — model potential returns
- **One-click sportsbook links** — act on opportunities instantly
- **Scan history tracking** — visualize market trends over time
- **Dark trading-terminal theme** — professional Bloomberg-style UI

## Tech Stack

- **Python** — Core logic and API integration
- **Streamlit** — Interactive web dashboard
- **Plotly** — Data visualization and charts
- **The Odds API** — Real-time odds data
- **Pandas** — Data processing

## The Math

An arbitrage exists when: (1/odds_A) + (1/odds_B) + (1/odds_C) < 1.0


Where each odds value comes from a DIFFERENT bookmaker.
The difference from 1.0 is your guaranteed profit margin.

## Live Demo

[🔗 Launch Dashboard](https://your-username-arbedge.streamlit.app)

## Setup

1. Clone this repo
2. `pip install -r requirements.txt`
3. Get a free API key from [the-odds-api.com](https://the-odds-api.com)
4. Update the API_KEY in `dashboard.py`
5. `streamlit run dashboard.py`

## Author

Built by [Mustaali Aamir Vasi] as a portfolio project combining AI, Data Engineering, and Finance.
