# =============================================================
# ARBEDGE — Sports Arbitrage Intelligence Dashboard
# =============================================================

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import json
import os
from datetime import datetime

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="ArbEdge — Sports Arbitrage Scanner",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CUSTOM CSS
# ============================================================
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
    }

    .main-header {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #00d4aa, #00a3ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
        line-height: 1.2;
    }

    .sub-header {
        font-size: 1rem;
        color: #6b7280;
        margin-top: 0;
    }

    .arb-card {
        background: linear-gradient(135deg, #0a2e1a, #1a4a2e);
        border: 2px solid #00d4aa;
        border-radius: 16px;
        padding: 24px;
        margin: 10px 0;
    }

    .arb-title {
        color: #00d4aa;
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .arb-details {
        color: #d1d5db;
        font-size: 0.95rem;
        line-height: 1.6;
    }

    .bet-leg {
        background: #1a1f2e;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #2d3548;
        text-align: center;
        margin: 5px 0;
    }

    .bet-leg-label {
        color: #6b7280;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .bet-leg-name {
        color: #ffffff;
        font-size: 1.1rem;
        font-weight: 700;
        margin: 6px 0;
    }

    .bet-leg-stake {
        color: #00d4aa;
        font-size: 1.8rem;
        font-weight: 800;
    }

    .bet-leg-odds {
        color: #9ca3af;
        font-size: 0.9rem;
        margin: 4px 0;
    }

    .book-btn {
        display: inline-block;
        padding: 10px 24px;
        margin: 6px 2px;
        border-radius: 10px;
        text-decoration: none;
        font-weight: 700;
        font-size: 0.9rem;
        color: white !important;
        transition: all 0.2s;
        border: none;
    }

    .book-btn:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }

    .btn-bet365 { background: linear-gradient(135deg, #027b5b, #03a678); }
    .btn-draftkings { background: linear-gradient(135deg, #3a9e26, #53d337); color: #000 !important; }
    .btn-betmgm { background: linear-gradient(135deg, #a68a3a, #c4a44a); color: #000 !important; }
    .btn-betway { background: linear-gradient(135deg, #008a20, #00c830); }
    .btn-fanduel { background: linear-gradient(135deg, #0f7ae5, #1493ff); }

    .profit-bar {
        text-align: center;
        margin: 15px 0;
        padding: 14px;
        background: linear-gradient(135deg, #0a2e1a, #0a3a1a);
        border-radius: 10px;
        border: 1px solid #1a4a2e;
    }

    .profit-label { color: #6b7280; font-size: 0.9rem; }
    .profit-value { color: #00d4aa; font-weight: 800; }
    .profit-big { font-size: 1.3rem; }

    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #ffffff;
        margin: 20px 0 10px 0;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)


# ============================================================
# SETTINGS
# ============================================================
API_KEY = "91723ff6468120c30188419ec8addd05"
BASE_URL = "https://api.the-odds-api.com/v4/sports"
REGIONS = "us,uk,eu,au"
ODDS_FORMAT = "decimal"

ALLOWED_BOOKMAKERS = {
    "bet365", "draftkings", "betmgm", "betway",
    "pointsbet (us)", "pointsbet", "fanduel",
}

SPORTS_CONFIG = {
    "soccer_epl": {"label": "Premier League", "emoji": "⚽"},
    "soccer_spain_la_liga": {"label": "La Liga", "emoji": "⚽"},
    "soccer_germany_bundesliga": {"label": "Bundesliga", "emoji": "⚽"},
    "soccer_italy_serie_a": {"label": "Serie A", "emoji": "⚽"},
    "soccer_france_ligue_one": {"label": "Ligue 1", "emoji": "⚽"},
    "soccer_uefa_champs_league": {"label": "Champions League", "emoji": "🏆"},
    "soccer_uefa_europa_league": {"label": "Europa League", "emoji": "🏆"},
    "mma_mixed_martial_arts": {"label": "UFC / MMA", "emoji": "🥊"},
    "basketball_nba": {"label": "NBA", "emoji": "🏀"},
    "icehockey_nhl": {"label": "NHL", "emoji": "🏒"},
}

SPORTSBOOK_INFO = {
    "bet365":         {"url": "https://www.bet365.com",            "css": "btn-bet365"},
    "Bet365":         {"url": "https://www.bet365.com",            "css": "btn-bet365"},
    "DraftKings":     {"url": "https://sportsbook.draftkings.com", "css": "btn-draftkings"},
    "BetMGM":         {"url": "https://sports.betmgm.com",         "css": "btn-betmgm"},
    "Betway":         {"url": "https://www.betway.com",            "css": "btn-betway"},
    "FanDuel":        {"url": "https://sportsbook.fanduel.com",    "css": "btn-fanduel"},
    "PointsBet (US)": {"url": "https://pointsbet.com",            "css": "btn-bet365"},
}

HISTORY_FILE = "scan_history.json"


# ============================================================
# SESSION STATE
# ============================================================
if "scan_done" not in st.session_state:
    st.session_state.scan_done = False
    st.session_state.arbs = []
    st.session_state.near_misses = []
    st.session_state.total_scans = 0
    st.session_state.total_arbs_ever = 0
    st.session_state.api_requests_used = 0
    st.session_state.last_scan_time = None
    st.session_state.total_opps_last = 0
    st.session_state.scan_history = []
    st.session_state.debug_log = []

    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                saved = json.load(f)
                st.session_state.scan_history = saved.get("history", [])
                st.session_state.total_scans = saved.get("total_scans", 0)
                st.session_state.total_arbs_ever = saved.get("total_arbs", 0)
                st.session_state.api_requests_used = saved.get("api_used", 0)
        except Exception:
            pass


def save_history():
    data = {
        "history": st.session_state.scan_history[-200:],
        "total_scans": st.session_state.total_scans,
        "total_arbs": st.session_state.total_arbs_ever,
        "api_used": st.session_state.api_requests_used,
    }
    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f)


# ============================================================
# API FUNCTIONS
# ============================================================
def fetch_odds(sport_key):
    try:
        url = f"{BASE_URL}/{sport_key}/odds"
        params = {
            "apiKey": API_KEY,
            "regions": REGIONS,
            "oddsFormat": ODDS_FORMAT,
            "markets": "h2h,spreads,totals",
        }
        resp = requests.get(url, params=params, timeout=15)

        if resp.status_code == 200:
            data = resp.json()
            return data, None
        elif resp.status_code == 422:
            params["markets"] = "h2h"
            resp2 = requests.get(url, params=params, timeout=15)
            if resp2.status_code == 200:
                return resp2.json(), None
            return [], f"Error {resp2.status_code}"
        elif resp.status_code == 429:
            return [], "API LIMIT REACHED"
        else:
            return [], f"Error {resp.status_code}"
    except Exception as e:
        return [], str(e)


def extract_opportunities(event):
    home = event["home_team"]
    away = event["away_team"]
    sport = event["sport_key"]
    start = event["commence_time"]
    match = f"{home} vs {away}"

    groups = {}
    for bm in event.get("bookmakers", []):
        name = bm["title"]
        if name.lower() not in ALLOWED_BOOKMAKERS:
            continue
        for mkt in bm.get("markets", []):
            mk = mkt["key"]
            for oc in mkt["outcomes"]:
                pt = oc.get("point", None)
                gk = (mk, pt)
                if gk not in groups:
                    groups[gk] = {}
                on = oc["name"]
                if on not in groups[gk]:
                    groups[gk][on] = []
                groups[gk][on].append((name, oc["price"]))

    opps = []
    for (mk, pt), outcomes in groups.items():
        books = set()
        for ol in outcomes.values():
            for bn, _ in ol:
                books.add(bn)
        if len(outcomes) < 2 or len(books) < 2:
            continue
        if mk == "h2h":
            ml = "Match Winner"
        elif mk == "spreads":
            ml = f"Spread ({pt})"
        elif mk == "totals":
            ml = f"Total ({pt})"
        else:
            ml = mk
        opps.append({
            "sport": sport, "match": match,
            "home_team": home, "away_team": away,
            "start_time": start, "market_key": mk,
            "point": pt, "market_label": ml,
            "outcomes": outcomes, "books": books,
        })
    return opps


def check_arb(opp, stake):
    outcomes = opp["outcomes"]
    best = {}
    for on, ol in outcomes.items():
        bb, bp = max(ol, key=lambda x: x[1])
        best[on] = {"bookmaker": bb, "odds": bp, "imp": 1.0 / bp}

    ti = sum(i["imp"] for i in best.values())
    margin = (1.0 / ti - 1.0) * 100.0

    result = {
        "sport": opp["sport"], "match": opp["match"],
        "home_team": opp["home_team"], "away_team": opp["away_team"],
        "start_time": opp["start_time"],
        "market_label": opp["market_label"],
        "market_key": opp["market_key"],
        "point": opp["point"],
        "best": best, "total_implied": ti,
        "margin": margin, "is_arb": ti < 1.0,
        "books_used": list(opp["books"]),
    }

    if ti < 1.0:
        gr = stake / ti
        profit = gr - stake
        stakes = {}
        for on, info in best.items():
            stakes[on] = round(gr / info["odds"], 2)
        result["return"] = round(gr, 2)
        result["profit"] = round(profit, 2)
        result["stakes"] = stakes

    return result


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("# ⚡ ArbEdge")
    st.markdown("*Sports Arbitrage Intelligence*")
    st.markdown("---")

    total_stake = st.slider(
        "💰 Max Stake per Arb",
        min_value=5, max_value=200, value=25, step=5,
        format="$%d",
    )

    st.markdown("---")
    st.markdown("### 🏆 Sports to Scan")
    selected_sports = []
    for key, config in SPORTS_CONFIG.items():
        label = f"{config['emoji']} {config['label']}"
        if st.checkbox(label, value=True, key=f"sport_{key}"):
            selected_sports.append(key)

    st.markdown("---")
    st.markdown("### 📱 Open Sportsbooks")
    book_links = {
        "bet365": "https://www.bet365.com",
        "DraftKings": "https://sportsbook.draftkings.com",
        "BetMGM": "https://sports.betmgm.com",
        "Betway": "https://www.betway.com",
        "FanDuel": "https://sportsbook.fanduel.com",
    }
    for name, url in book_links.items():
        st.link_button(f"🔗 {name}", url, use_container_width=True)

    st.markdown("---")
    st.markdown("### 📊 API Budget")
    used = st.session_state.api_requests_used
    remaining = max(500 - used, 0)
    st.progress(min(used / 500, 1.0))
    st.caption(f"{used} used · {remaining} remaining · 500/month")

    if remaining < 50:
        st.warning("Running low on API requests!")


# ============================================================
# HEADER + SCAN BUTTON
# ============================================================
col_title, col_scan = st.columns([3, 1])

with col_title:
    st.markdown('<p class="main-header">⚡ ArbEdge</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">'
        'Real-Time Sports Arbitrage Scanner — Ontario Sportsbooks'
        '</p>',
        unsafe_allow_html=True,
    )

with col_scan:
    st.markdown("<br>", unsafe_allow_html=True)
    scan_clicked = st.button(
        "🔍 SCAN NOW",
        use_container_width=True,
        type="primary",
    )


# ============================================================
# SCAN LOGIC
# ============================================================
if scan_clicked:
    if not selected_sports:
        st.warning("Select at least one sport in the sidebar!")
    else:
        arbs = []
        near_misses = []
        total_opps = 0
        api_used = 0
        debug_msgs = []

        progress = st.progress(0, text="Starting scan...")
        status_text = st.empty()

        for i, sport in enumerate(selected_sports):
            sport_label = SPORTS_CONFIG.get(sport, {}).get("label", sport)
            progress.progress(
                (i + 1) / len(selected_sports),
                text=f"Scanning {sport_label}...",
            )
            status_text.caption(f"Fetching odds for {sport_label}...")

            data, error = fetch_odds(sport)
            api_used += 1

            if error:
                debug_msgs.append(f"  {sport_label}: {error}")
                continue

            if not data:
                debug_msgs.append(f"  {sport_label}: No events")
                continue

            event_count = len(data)
            sport_opps = 0

            for event in data:
                opps = extract_opportunities(event)
                for opp in opps:
                    total_opps += 1
                    sport_opps += 1
                    result = check_arb(opp, total_stake)
                    if result["is_arb"]:
                        arbs.append(result)
                    else:
                        near_misses.append(result)

            debug_msgs.append(
                f"  {sport_label}: {event_count} events, "
                f"{sport_opps} opportunities"
            )

        progress.empty()
        status_text.empty()

        arbs.sort(key=lambda x: x["margin"], reverse=True)
        near_misses.sort(key=lambda x: x["total_implied"])

        # Update session state
        st.session_state.scan_done = True
        st.session_state.arbs = arbs
        st.session_state.near_misses = near_misses
        st.session_state.total_scans += 1
        st.session_state.total_arbs_ever += len(arbs)
        st.session_state.api_requests_used += api_used
        st.session_state.last_scan_time = datetime.now().strftime("%I:%M:%S %p")
        st.session_state.total_opps_last = total_opps
        st.session_state.debug_log = debug_msgs

        closest = near_misses[0]["margin"] if near_misses else 0
        st.session_state.scan_history.append({
            "time": datetime.now().strftime("%H:%M"),
            "arbs": len(arbs),
            "closest": round(closest, 2),
            "opps": total_opps,
        })

        save_history()

        if arbs:
            st.balloons()


# ============================================================
# SCAN RESULTS SECTION
# ============================================================
if st.session_state.scan_done:

    st.markdown("---")

    # Metrics row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("🔄 Total Scans", st.session_state.total_scans)
    with m2:
        st.metric("🔥 Arbs Found", st.session_state.total_arbs_ever)
    with m3:
        closest_val = 0.0
        if st.session_state.near_misses:
            closest_val = st.session_state.near_misses[0]["margin"]
        st.metric("🎯 Nearest Margin", f"{closest_val:.2f}%")
    with m4:
        st.metric("🕐 Last Scan", st.session_state.last_scan_time or "—")

    # Scan debug info (expandable)
    with st.expander(
        f"📡 Scan Details — {st.session_state.total_opps_last} opportunities checked",
        expanded=False,
    ):
        for msg in st.session_state.debug_log:
            st.text(msg)

    st.markdown("---")

    # ========================================================
    # ARBS FOUND
    # ========================================================
    if st.session_state.arbs:
        st.markdown(
            '<p class="section-header">🔥 LIVE ARBITRAGE OPPORTUNITIES</p>',
            unsafe_allow_html=True,
        )

        for idx, arb in enumerate(st.session_state.arbs):
            sport_info = SPORTS_CONFIG.get(
                arb["sport"], {"label": arb["sport"], "emoji": "🏅"}
            )

            st.markdown(f"""
            <div class="arb-card">
                <div class="arb-title">
                    💰 ARBITRAGE #{idx + 1} — {arb['match']}
                </div>
                <div class="arb-details">
                    <strong>{sport_info['emoji']} {sport_info['label']}</strong>
                    &nbsp;·&nbsp;
                    <strong>Market:</strong> {arb['market_label']}
                    &nbsp;·&nbsp;
                    <strong>Margin:</strong> +{arb['margin']:.2f}%
                    &nbsp;·&nbsp;
                    <strong>Profit:</strong> ${arb['profit']:.2f}
                </div>
            </div>
            """, unsafe_allow_html=True)

            num_outcomes = len(arb["best"])
            cols = st.columns(num_outcomes)

            for j, (outcome, info) in enumerate(arb["best"].items()):
                stake_val = arb["stakes"][outcome]
                book = info["bookmaker"]
                odds = info["odds"]
                book_info = SPORTSBOOK_INFO.get(
                    book, {"url": "#", "css": "btn-bet365"}
                )

                display_name = outcome
                if arb["market_key"] == "totals":
                    display_name = f"{outcome} {arb['point']}"
                elif arb["market_key"] == "spreads":
                    display_name = f"{outcome} ({arb['point']})"

                with cols[j]:
                    st.markdown(f"""
                    <div class="bet-leg">
                        <div class="bet-leg-label">Bet On</div>
                        <div class="bet-leg-name">{display_name}</div>
                        <div class="bet-leg-stake">${stake_val:.2f}</div>
                        <div class="bet-leg-odds">@ odds {odds:.2f}</div>
                        <a href="{book_info['url']}" target="_blank"
                           class="book-btn {book_info['css']}">
                            Open {book} →
                        </a>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="profit-bar">
                <span class="profit-label">Total Bet: </span>
                <span class="profit-value">${total_stake:.2f}</span>
                &nbsp;&nbsp;→&nbsp;&nbsp;
                <span class="profit-label">Return: </span>
                <span class="profit-value">${arb['return']:.2f}</span>
                &nbsp;&nbsp;→&nbsp;&nbsp;
                <span class="profit-label">Profit: </span>
                <span class="profit-value profit-big">
                    ${arb['profit']:.2f} ✓
                </span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("")

        st.markdown("---")

    else:
        st.info(
            "📡 No arbitrage opportunities right now. "
            "Check the near-misses below — odds shift constantly!"
        )

    # ========================================================
    # CHARTS
    # ========================================================
    if st.session_state.near_misses:

        chart_left, chart_right = st.columns([1, 1])

        # ARB RADAR GAUGE
        with chart_right:
            st.markdown(
                '<p class="section-header">🎯 Arb Radar</p>',
                unsafe_allow_html=True,
            )

            closest_margin = st.session_state.near_misses[0]["margin"]

            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=closest_margin,
                number={"suffix": "%", "font": {"size": 48, "color": "white"}},
                gauge={
                    "axis": {
                        "range": [-8, 3],
                        "tickfont": {"color": "#6b7280"},
                        "dtick": 1,
                    },
                    "bar": {
                        "color": "#00d4aa" if closest_margin >= 0 else "#ffa500",
                        "thickness": 0.3,
                    },
                    "bgcolor": "#1a1f2e",
                    "borderwidth": 0,
                    "steps": [
                        {"range": [-8, -4], "color": "#1f1215"},
                        {"range": [-4, -2], "color": "#2a1f0e"},
                        {"range": [-2, -0.5], "color": "#1f2a0e"},
                        {"range": [-0.5, 0], "color": "#0e2a15"},
                        {"range": [0, 3], "color": "#0a3a1a"},
                    ],
                    "threshold": {
                        "line": {"color": "#00d4aa", "width": 4},
                        "thickness": 0.8,
                        "value": 0,
                    },
                },
                title={
                    "text": "Closest to Arb Territory",
                    "font": {"color": "#6b7280", "size": 13},
                },
            ))

            fig_gauge.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=320,
                margin=dict(t=100, b=30, l=40, r=40),
            )

            st.plotly_chart(fig_gauge, use_container_width=True)

            if closest_margin >= 0:
                st.success("🔥 ARB AVAILABLE — Act now!")
            elif closest_margin > -1:
                st.warning("⚡ Very close! Scan again in a few minutes.")
            elif closest_margin > -3:
                st.info("📡 Odds are moving. Keep scanning.")
            else:
                st.caption("Market is stable. Arbs may appear closer to match time.")

        # MARGINS BY SPORT
        with chart_left:
            st.markdown(
                '<p class="section-header">📊 Margins by Sport</p>',
                unsafe_allow_html=True,
            )

            sport_data = {}
            for nm in st.session_state.near_misses:
                si = SPORTS_CONFIG.get(
                    nm["sport"], {"label": nm["sport"], "emoji": "🏅"}
                )
                label = f"{si['emoji']} {si['label']}"
                if label not in sport_data:
                    sport_data[label] = []
                sport_data[label].append(nm["margin"])

            chart_rows = []
            for sl, margins in sport_data.items():
                chart_rows.append({
                    "Sport": sl,
                    "Best Margin (%)": max(margins),
                    "Count": len(margins),
                })

            chart_df = pd.DataFrame(chart_rows).sort_values(
                "Best Margin (%)", ascending=True
            )

            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(
                y=chart_df["Sport"],
                x=chart_df["Best Margin (%)"],
                orientation="h",
                marker=dict(
                    color=chart_df["Best Margin (%)"],
                    colorscale=[
                        [0, "#ef4444"], [0.4, "#f97316"],
                        [0.7, "#fbbf24"], [1.0, "#00d4aa"],
                    ],
                    cmin=-8, cmax=1,
                ),
                text=[f"{v:.1f}%" for v in chart_df["Best Margin (%)"]],
                textposition="outside",
                textfont=dict(color="#d1d5db", size=12),
            ))

            fig_bar.add_vline(
                x=0, line_color="#00d4aa",
                line_width=2, line_dash="dash",
                annotation_text="ARB →",
                annotation_font_color="#00d4aa",
            )

            fig_bar.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#6b7280",
                height=320,
                margin=dict(t=20, b=40, l=20, r=60),
                showlegend=False,
                xaxis=dict(title="Best Margin (%)", gridcolor="#1a1f2e"),
                yaxis=dict(title=""),
            )

            st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("---")

        # ====================================================
        # NEAR MISSES TABLE
        # ====================================================
        st.markdown(
            '<p class="section-header">📋 Top 20 Near-Miss Opportunities</p>',
            unsafe_allow_html=True,
        )
        st.caption("When margin crosses above 0%, it becomes guaranteed profit.")

        nm_rows = []
        for nm in st.session_state.near_misses[:20]:
            si = SPORTS_CONFIG.get(
                nm["sport"], {"label": nm["sport"], "emoji": "🏅"}
            )
            m = nm["margin"]
            if m > -1:
                status = "🟢"
            elif m > -3:
                status = "🟡"
            else:
                status = "🔴"

            odds_parts = []
            for on, info in nm["best"].items():
                dn = on
                if nm["market_key"] == "totals":
                    dn = f"{on} {nm['point']}"
                elif nm["market_key"] == "spreads":
                    dn = f"{on} ({nm['point']})"
                odds_parts.append(
                    f"{dn}: {info['odds']:.2f} @ {info['bookmaker']}"
                )

            nm_rows.append({
                "": status,
                "Margin": f"{m:.2f}%",
                "Match": nm["match"],
                "Sport": f"{si['emoji']} {si['label']}",
                "Market": nm["market_label"],
                "Best Odds": " | ".join(odds_parts),
            })

        if nm_rows:
            nm_df = pd.DataFrame(nm_rows)
            st.dataframe(nm_df, use_container_width=True, hide_index=True, height=500)

        st.markdown("---")

    # ========================================================
    # SCAN HISTORY
    # ========================================================
    if len(st.session_state.scan_history) > 1:
        st.markdown(
            '<p class="section-header">📈 Scan History</p>',
            unsafe_allow_html=True,
        )

        hist_df = pd.DataFrame(st.session_state.scan_history)

        fig_hist = go.Figure()
        fig_hist.add_trace(go.Scatter(
            x=hist_df["time"],
            y=hist_df["closest"],
            mode="lines+markers",
            name="Closest Margin",
            line=dict(color="#ffa500", width=2),
            marker=dict(size=6),
            fill="tozeroy",
            fillcolor="rgba(255, 165, 0, 0.1)",
        ))

        fig_hist.add_hline(
            y=0, line_color="#00d4aa",
            line_width=2, line_dash="dash",
            annotation_text="Arb Threshold",
            annotation_font_color="#00d4aa",
        )

        arb_points = hist_df[hist_df["arbs"] > 0]
        if not arb_points.empty:
            fig_hist.add_trace(go.Scatter(
                x=arb_points["time"],
                y=arb_points["closest"],
                mode="markers",
                name="Arb Found!",
                marker=dict(color="#00d4aa", size=14, symbol="star"),
            ))

        fig_hist.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#6b7280",
            height=300,
            margin=dict(t=20, b=40, l=40, r=20),
            xaxis=dict(title="Time", gridcolor="#1a1f2e"),
            yaxis=dict(title="Closest Margin (%)", gridcolor="#1a1f2e"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(color="#d1d5db")),
        )

        st.plotly_chart(fig_hist, use_container_width=True)

        st.markdown("---")

    # ========================================================
    # PROFIT SIMULATOR
    # ========================================================
    if st.session_state.near_misses:
        st.markdown(
            '<p class="section-header">🧮 Profit Simulator</p>',
            unsafe_allow_html=True,
        )
        st.caption("See potential profit at different stake and margin levels.")

        sim_c1, sim_c2 = st.columns([1, 2])

        with sim_c1:
            sim_stake = st.slider(
                "Simulated Stake", min_value=5, max_value=500,
                value=25, step=5, format="$%d", key="sim_stake",
            )
            sim_margin = st.slider(
                "If margin were...", min_value=0.1, max_value=5.0,
                value=1.0, step=0.1, format="%.1f%%", key="sim_margin",
            )

        with sim_c2:
            sim_return = sim_stake / (1 - sim_margin / 100)
            sim_profit = sim_return - sim_stake
            profits = [sim_profit * n for n in [1, 3, 5, 10]]
            labels = ["1 arb/day", "3 arbs/day", "5 arbs/day", "10 arbs/day"]

            fig_sim = go.Figure()
            fig_sim.add_trace(go.Bar(
                x=labels, y=profits,
                marker_color=["#00d4aa", "#00c49a", "#00a3ff", "#0088dd"],
                text=[f"${p:.2f}" for p in profits],
                textposition="outside",
                textfont=dict(color="#d1d5db", size=14),
            ))
            fig_sim.update_layout(
                title=dict(
                    text=f"Daily Profit at ${sim_stake}, {sim_margin:.1f}% margin",
                    font=dict(color="#d1d5db", size=14),
                ),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#6b7280",
                height=280,
                margin=dict(t=60, b=40, l=40, r=20),
                xaxis=dict(gridcolor="#1a1f2e"),
                yaxis=dict(title="Daily Profit ($)", gridcolor="#1a1f2e"),
            )
            st.plotly_chart(fig_sim, use_container_width=True)

else:
    # ========================================================
    # WELCOME SCREEN (before first scan)
    # ========================================================
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 60px 0;">
        <p style="font-size: 3rem; margin-bottom: 10px;">⚡</p>
        <p style="font-size: 1.5rem; color: #d1d5db; font-weight: 700;">
            Welcome to ArbEdge
        </p>
        <p style="color: #6b7280; max-width: 500px; margin: 0 auto;">
            Click <strong>🔍 SCAN NOW</strong> above to fetch live odds
            from Ontario sportsbooks and detect arbitrage opportunities
            in real-time.
        </p>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# FOOTER
# ============================================================
st.markdown("""
<div style="text-align: center; padding: 30px 0; color: #4b5563;">
    <strong>ArbEdge</strong> — Built with Python, Streamlit & The Odds API<br>
    <span style="font-size: 0.8rem;">
        Sports arbitrage scanner for Ontario-licensed sportsbooks.
        For educational and portfolio purposes.
    </span>
</div>
""", unsafe_allow_html=True)
