import streamlit as st
import sqlite3
import os
import json
import base64
import tempfile
import requests
from pathlib import Path
import pandas as pd
from datetime import datetime
import io

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="StartupLens AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

:root {
    --bg: #0a0a0f;
    --surface: #12121a;
    --surface2: #1a1a26;
    --accent: #7c5cfc;
    --accent2: #fc5c7d;
    --text: #e8e8f0;
    --muted: #6b6b80;
    --border: #252535;
    --success: #22d3a4;
    --warning: #f59e0b;
    --danger: #ef4444;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg);
    color: var(--text);
}

h1, h2, h3, h4 {
    font-family: 'Syne', sans-serif;
}

/* Hide Streamlit branding */
#MainMenu, footer, header {visibility: hidden;}
.stDeployButton {display: none;}

/* Main header */
.hero {
    background: linear-gradient(135deg, #0a0a0f 0%, #1a0a2e 50%, #0a0a0f 100%);
    border-bottom: 1px solid var(--border);
    padding: 2.5rem 2rem 2rem;
    margin: -1rem -1rem 2rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -20%;
    width: 60%;
    height: 200%;
    background: radial-gradient(ellipse, rgba(124,92,252,0.12) 0%, transparent 70%);
    pointer-events: none;
}
.hero::after {
    content: '';
    position: absolute;
    top: -50%;
    right: -20%;
    width: 50%;
    height: 200%;
    background: radial-gradient(ellipse, rgba(252,92,125,0.08) 0%, transparent 70%);
    pointer-events: none;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.4rem;
    font-weight: 800;
    background: linear-gradient(135deg, #fff 30%, #7c5cfc 70%, #fc5c7d 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 0.4rem;
    letter-spacing: -0.03em;
}
.hero-sub {
    color: var(--muted);
    font-size: 1rem;
    font-weight: 300;
    letter-spacing: 0.02em;
}

/* Cards */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: border-color 0.2s, box-shadow 0.2s;
}
.card:hover {
    border-color: rgba(124,92,252,0.4);
    box-shadow: 0 0 20px rgba(124,92,252,0.08);
}
.card-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1rem;
}
.card-icon {
    width: 38px; height: 38px;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
    background: linear-gradient(135deg, rgba(124,92,252,0.2), rgba(252,92,125,0.1));
    border: 1px solid rgba(124,92,252,0.3);
}
.card-title {
    font-family: 'Syne', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: var(--text);
    margin: 0;
}

/* Score badge */
.score-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.3rem 0.9rem;
    border-radius: 999px;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 0.85rem;
    letter-spacing: 0.02em;
}
.score-high { background: rgba(34,211,164,0.15); color: #22d3a4; border: 1px solid rgba(34,211,164,0.3);}
.score-mid  { background: rgba(245,158,11,0.15); color: #f59e0b; border: 1px solid rgba(245,158,11,0.3);}
.score-low  { background: rgba(239,68,68,0.15);  color: #ef4444; border: 1px solid rgba(239,68,68,0.3);}

/* Startup list item */
.startup-item {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.6rem;
    cursor: pointer;
    transition: all 0.15s;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.startup-item:hover {
    border-color: rgba(124,92,252,0.5);
    background: var(--surface2);
}
.startup-name {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 0.95rem;
}
.startup-tag {
    font-size: 0.75rem;
    color: var(--muted);
    margin-top: 0.1rem;
}

/* Section label */
.section-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}

/* Advice blocks */
.advice-block {
    background: var(--surface2);
    border-left: 3px solid var(--accent);
    border-radius: 0 8px 8px 0;
    padding: 1rem 1.2rem;
    margin-bottom: 0.75rem;
    font-size: 0.9rem;
    line-height: 1.65;
}
.advice-warning {
    border-left-color: var(--warning);
}
.advice-danger {
    border-left-color: var(--danger);
}
.advice-success {
    border-left-color: var(--success);
}

/* Metric pills */
.metric-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin: 0.5rem 0;
}
.metric-pill {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 0.3rem 0.7rem;
    font-size: 0.78rem;
    color: var(--muted);
}
.metric-pill span {
    color: var(--text);
    font-weight: 500;
    margin-left: 0.3rem;
}

/* Streamlit overrides */
.stButton > button {
    background: linear-gradient(135deg, var(--accent), #6040e0) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 0.55rem 1.4rem !important;
    transition: opacity 0.15s !important;
}
.stButton > button:hover { opacity: 0.88 !important; }

div[data-testid="stFileUploader"] {
    background: var(--surface) !important;
    border: 1px dashed var(--border) !important;
    border-radius: 10px !important;
}

.stTextInput input, .stTextArea textarea, .stSelectbox select {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
}

.stExpander {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] .stMarkdown { color: var(--muted) !important; }

/* Tab overrides */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border-radius: 8px !important;
    padding: 0.2rem !important;
    gap: 0.2rem !important;
    border: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--muted) !important;
    border-radius: 6px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
}
.stTabs [aria-selected="true"] {
    background: var(--accent) !important;
    color: white !important;
}

.stSpinner > div { border-top-color: var(--accent) !important; }

/* Loading shimmer */
@keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}
.shimmer {
    background: linear-gradient(90deg, var(--surface) 25%, var(--surface2) 50%, var(--surface) 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
    border-radius: 6px;
    height: 14px;
    margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)

# ── Database ──────────────────────────────────────────────────────────────────
DB_PATH = "startups.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS startups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT NOT NULL,
            tagline TEXT,
            full_description TEXT,
            category TEXT,
            target_funding REAL,
            website_url TEXT,
            team_size INTEGER,
            target_market TEXT,
            competition_analysis TEXT,
            revenue_model TEXT,
            current_stage TEXT,
            current_customers TEXT,
            pitch_deck BLOB,
            pitch_deck_name TEXT,
            business_plan BLOB,
            business_plan_name TEXT,
            financial_projections BLOB,
            financial_projections_name TEXT,
            product_demo BLOB,
            product_demo_name TEXT,
            created_at TEXT,
            last_evaluated TEXT,
            evaluation_result TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_all_startups():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT id, project_name, tagline, category, current_stage, target_funding, created_at, last_evaluated FROM startups ORDER BY created_at DESC",
        conn
    )
    conn.close()
    return df

def get_startup_by_id(sid):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM startups WHERE id=?", (sid,))
    row = c.fetchone()
    cols = [d[0] for d in c.description]
    conn.close()
    return dict(zip(cols, row)) if row else None

def save_startup(data: dict):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO startups (
            project_name, tagline, full_description, category, target_funding,
            website_url, team_size, target_market, competition_analysis,
            revenue_model, current_stage, current_customers,
            pitch_deck, pitch_deck_name, business_plan, business_plan_name,
            financial_projections, financial_projections_name,
            product_demo, product_demo_name, created_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        data['project_name'], data['tagline'], data['full_description'],
        data['category'], data['target_funding'], data['website_url'],
        data['team_size'], data['target_market'], data['competition_analysis'],
        data['revenue_model'], data['current_stage'], data['current_customers'],
        data.get('pitch_deck'), data.get('pitch_deck_name'),
        data.get('business_plan'), data.get('business_plan_name'),
        data.get('financial_projections'), data.get('financial_projections_name'),
        data.get('product_demo'), data.get('product_demo_name'),
        datetime.now().isoformat()
    ))
    conn.commit()
    sid = c.lastrowid
    conn.close()
    return sid

def update_evaluation(sid, result_json):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "UPDATE startups SET evaluation_result=?, last_evaluated=? WHERE id=?",
        (result_json, datetime.now().isoformat(), sid)
    )
    conn.commit()
    conn.close()

def delete_startup(sid):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM startups WHERE id=?", (sid,))
    conn.commit()
    conn.close()

# ── Mistral AI ────────────────────────────────────────────────────────────────
MISTRAL_KEY = st.secrets["MpDjSDtazDWPTD1v75zLhpY77rAFF0qI"]
def build_prompt(s: dict) -> str:
    files_present = []
    if s.get('pitch_deck'):        files_present.append("Pitch Deck")
    if s.get('business_plan'):     files_present.append("Business Plan")
    if s.get('financial_projections'): files_present.append("Financial Projections")
    if s.get('product_demo'):      files_present.append("Product Demo")

    return f"""You are a world-class startup advisor, venture capitalist, and business strategist with 20+ years of experience evaluating startups across all industries.

Evaluate the following startup thoroughly and provide expert-level strategic advice. Be specific, actionable, and brutally honest — but constructive.

═══════════════════════════════════════════════
STARTUP PROFILE
═══════════════════════════════════════════════
Project Name:         {s.get('project_name', 'N/A')}
Tagline:              {s.get('tagline', 'N/A')}
Category:             {s.get('category', 'N/A')}
Current Stage:        {s.get('current_stage', 'N/A')}
Website:              {s.get('website_url', 'N/A')}
Team Size:            {s.get('team_size', 'N/A')}
Target Funding:       ${s.get('target_funding', 'N/A'):,} USD
Current Customers:    {s.get('current_customers', 'N/A')}

FULL DESCRIPTION:
{s.get('full_description', 'N/A')}

TARGET MARKET:
{s.get('target_market', 'N/A')}

COMPETITION ANALYSIS:
{s.get('competition_analysis', 'N/A')}

REVENUE MODEL:
{s.get('revenue_model', 'N/A')}

FILES PROVIDED: {', '.join(files_present) if files_present else 'None uploaded'}
═══════════════════════════════════════════════

Respond ONLY with a valid JSON object (no markdown, no backticks) with this exact structure:

{{
  "overall_score": <integer 0-100>,
  "investment_readiness": <"Not Ready" | "Early Stage" | "Nearly There" | "Investment Ready">,
  "executive_summary": "<2-3 sentence sharp summary of the startup>",
  "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
  "weaknesses": ["<weakness 1>", "<weakness 2>", "<weakness 3>"],
  "scores": {{
    "market_opportunity": <0-10>,
    "team_strength": <0-10>,
    "product_innovation": <0-10>,
    "revenue_model": <0-10>,
    "competitive_position": <0-10>,
    "traction": <0-10>,
    "funding_readiness": <0-10>
  }},
  "advice": {{
    "pitch_improvement": "<detailed expert advice on improving pitch and messaging>",
    "market_strategy": "<detailed go-to-market strategy advice>",
    "product_roadmap": "<product development and roadmap recommendations>",
    "fundraising": "<fundraising strategy, which VCs to target, how to approach them>",
    "team_building": "<team gaps and hiring priorities>",
    "revenue_acceleration": "<specific revenue growth tactics>",
    "risk_mitigation": "<top 3 risks and how to mitigate them>",
    "competitive_moat": "<how to build defensible competitive advantage>",
    "milestones": "<key milestones to hit in next 6 and 12 months>"
  }},
  "investor_verdict": "<What a VC would say about this startup in one frank paragraph>",
  "next_steps": ["<immediate action 1>", "<immediate action 2>", "<immediate action 3>", "<immediate action 4>", "<immediate action 5>"]
}}"""
def call_mistral(prompt: str) -> str:
    if not MISTRAL_KEY:
        raise ValueError(
            "MISTRAL_API_KEY not found in Streamlit secrets."
        )

    headers = {
        "Authorization": f"Bearer {MISTRAL_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistral-large-latest",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3,
        "max_tokens": 3000
    }

    response = requests.post(
        "https://api.mistral.ai/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=120
    )

    if response.status_code != 200:
        raise Exception(
            f"Mistral API Error ({response.status_code}): {response.text}"
        )

    data = response.json()

    if "choices" not in data:
        raise Exception(
            f"Unexpected API response: {json.dumps(data)}"
        )

    return data["choices"][0]["message"]["content"]
def evaluate_startup(s: dict) -> dict:
    prompt = build_prompt(s)

    raw = call_mistral(prompt).strip()

    if raw.startswith("```json"):
        raw = raw.replace("```json", "", 1)

    if raw.startswith("```"):
        raw = raw.replace("```", "", 1)

    if raw.endswith("```"):
        raw = raw[:-3]

    raw = raw.strip()

    try:
        return json.loads(raw)

    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}")

        if start != -1 and end != -1:
            cleaned = raw[start:end + 1]
            return json.loads(cleaned)

        raise

# ── UI Helpers ────────────────────────────────────────────────────────────────
def score_color(score):
    if score >= 70: return "score-high"
    if score >= 40: return "score-mid"
    return "score-low"

def score_emoji(score):
    if score >= 70: return "✦"
    if score >= 40: return "◈"
    return "◇"

def render_score_bar(label, value, max_val=10):
    pct = (value / max_val) * 100
    color = "#22d3a4" if pct >= 70 else "#f59e0b" if pct >= 40 else "#ef4444"
    st.markdown(f"""
    <div style="margin-bottom:0.7rem;">
      <div style="display:flex;justify-content:space-between;margin-bottom:0.25rem;">
        <span style="font-size:0.82rem;color:#a0a0b8;">{label}</span>
        <span style="font-size:0.82rem;font-weight:700;color:{color};">{value}/10</span>
      </div>
      <div style="height:5px;background:#1a1a26;border-radius:99px;overflow:hidden;">
        <div style="height:100%;width:{pct}%;background:{color};border-radius:99px;transition:width 0.6s ease;"></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

def render_evaluation(ev: dict):
    score = ev.get("overall_score", 0)
    cls = score_color(score)

    # Header row
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"""
        <div style="margin-bottom:1.5rem;">
          <div style="font-family:'Syne',sans-serif;font-size:1.6rem;font-weight:800;margin-bottom:0.3rem;">{ev.get('investment_readiness','')}</div>
          <div style="color:#6b6b80;font-size:0.9rem;line-height:1.6;">{ev.get('executive_summary','')}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="text-align:center;padding:1rem;background:#12121a;border:1px solid #252535;border-radius:12px;">
          <div style="font-family:'Syne',sans-serif;font-size:3rem;font-weight:800;
               background:linear-gradient(135deg,#7c5cfc,#fc5c7d);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            {score}
          </div>
          <div style="font-size:0.7rem;letter-spacing:0.1em;color:#6b6b80;text-transform:uppercase;font-weight:600;">Overall Score</div>
        </div>
        """, unsafe_allow_html=True)

    tabs = st.tabs(["📊 Scores", "💪 Strengths & Weaknesses", "🎯 Expert Advice", "🗺️ Next Steps", "💬 Investor Verdict"])

    with tabs[0]:
        st.markdown('<div class="section-label">Dimension Scores</div>', unsafe_allow_html=True)
        scores = ev.get("scores", {})
        labels = {
            "market_opportunity": "Market Opportunity",
            "team_strength": "Team Strength",
            "product_innovation": "Product Innovation",
            "revenue_model": "Revenue Model",
            "competitive_position": "Competitive Position",
            "traction": "Traction",
            "funding_readiness": "Funding Readiness",
        }
        for key, label in labels.items():
            render_score_bar(label, scores.get(key, 0))

    with tabs[1]:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="section-label">Strengths</div>', unsafe_allow_html=True)
            for s in ev.get("strengths", []):
                st.markdown(f'<div class="advice-block advice-success">✦ {s}</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="section-label">Weaknesses</div>', unsafe_allow_html=True)
            for w in ev.get("weaknesses", []):
                st.markdown(f'<div class="advice-block advice-danger">◇ {w}</div>', unsafe_allow_html=True)

    with tabs[2]:
        advice = ev.get("advice", {})
        advice_config = [
            ("pitch_improvement",     "🎤 Pitch Improvement",         ""),
            ("market_strategy",       "🌍 Market Strategy",           ""),
            ("product_roadmap",       "🛠️ Product Roadmap",           ""),
            ("fundraising",           "💰 Fundraising Strategy",      ""),
            ("team_building",         "👥 Team Building",             "warning"),
            ("revenue_acceleration",  "📈 Revenue Acceleration",      ""),
            ("risk_mitigation",       "⚠️ Risk Mitigation",           "danger"),
            ("competitive_moat",      "🏰 Competitive Moat",          ""),
            ("milestones",            "🎯 Key Milestones",            ""),
        ]
        for key, label, cls_suffix in advice_config:
            if advice.get(key):
                extra = f" advice-{cls_suffix}" if cls_suffix else ""
                st.markdown(f"""
                <div class="section-label" style="margin-top:1rem;">{label}</div>
                <div class="advice-block{extra}">{advice[key]}</div>
                """, unsafe_allow_html=True)

    with tabs[3]:
        st.markdown('<div class="section-label">Immediate Action Plan</div>', unsafe_allow_html=True)
        for i, step in enumerate(ev.get("next_steps", []), 1):
            st.markdown(f"""
            <div style="display:flex;gap:0.9rem;align-items:flex-start;margin-bottom:0.7rem;
                 background:#12121a;border:1px solid #252535;border-radius:10px;padding:0.9rem 1rem;">
              <div style="min-width:26px;height:26px;border-radius:6px;
                   background:linear-gradient(135deg,#7c5cfc,#6040e0);
                   display:flex;align-items:center;justify-content:center;
                   font-family:'Syne',sans-serif;font-weight:700;font-size:0.78rem;color:white;">
                {i:02d}
              </div>
              <div style="font-size:0.88rem;line-height:1.55;padding-top:2px;">{step}</div>
            </div>
            """, unsafe_allow_html=True)

    with tabs[4]:
        verdict = ev.get("investor_verdict", "")
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#12121a,#1a1226);
             border:1px solid rgba(124,92,252,0.25);border-radius:12px;padding:1.8rem;
             font-size:1rem;line-height:1.75;color:#c8c8e0;font-style:italic;
             position:relative;">
          <div style="position:absolute;top:-0.6rem;left:1.5rem;
               background:#0a0a0f;padding:0 0.5rem;
               font-family:'Syne',sans-serif;font-size:0.7rem;
               letter-spacing:0.1em;text-transform:uppercase;color:#7c5cfc;font-style:normal;">
            VC Perspective
          </div>
          "{verdict}"
        </div>
        """, unsafe_allow_html=True)

# ── Init ──────────────────────────────────────────────────────────────────────
init_db()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-title">StartupLens AI</div>
  <div class="hero-sub">Expert-grade startup evaluation powered by Mistral AI</div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar nav ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="font-family:'Syne',sans-serif;font-size:1rem;font-weight:700;
         margin-bottom:1.2rem;color:#e8e8f0;">Navigation</div>
    """, unsafe_allow_html=True)
    page = st.radio("", ["📋 All Startups", "➕ Add Startup", "🔍 Evaluate"], label_visibility="collapsed")
    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.72rem;color:#3d3d50;line-height:1.6;">
    Powered by Mistral Large<br>
    Evaluates: pitch, market, team,<br>revenue, competitive position,<br>funding readiness & more.
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: ALL STARTUPS
# ══════════════════════════════════════════════════════════════════════════════
if page == "📋 All Startups":
    df = get_all_startups()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="card" style="text-align:center;">
          <div style="font-family:'Syne',sans-serif;font-size:2.5rem;font-weight:800;
               background:linear-gradient(135deg,#7c5cfc,#fc5c7d);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            {len(df)}
          </div>
          <div style="font-size:0.78rem;color:#6b6b80;letter-spacing:0.05em;">TOTAL STARTUPS</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        evaluated = df['last_evaluated'].notna().sum()
        st.markdown(f"""
        <div class="card" style="text-align:center;">
          <div style="font-family:'Syne',sans-serif;font-size:2.5rem;font-weight:800;color:#22d3a4;">
            {evaluated}
          </div>
          <div style="font-size:0.78rem;color:#6b6b80;letter-spacing:0.05em;">EVALUATED</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        pending = len(df) - evaluated
        st.markdown(f"""
        <div class="card" style="text-align:center;">
          <div style="font-family:'Syne',sans-serif;font-size:2.5rem;font-weight:800;color:#f59e0b;">
            {pending}
          </div>
          <div style="font-size:0.78rem;color:#6b6b80;letter-spacing:0.05em;">PENDING REVIEW</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-label" style="margin-top:1.5rem;">Startup Registry</div>', unsafe_allow_html=True)

    if df.empty:
        st.markdown("""
        <div style="text-align:center;padding:3rem;color:#3d3d50;">
          <div style="font-size:2.5rem;margin-bottom:0.5rem;">🚀</div>
          <div style="font-family:'Syne',sans-serif;font-size:1rem;font-weight:700;color:#6b6b80;">No startups yet</div>
          <div style="font-size:0.82rem;color:#3d3d50;margin-top:0.3rem;">Add your first startup using the sidebar</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for _, row in df.iterrows():
            ev_status = "✓ Evaluated" if pd.notna(row['last_evaluated']) and row['last_evaluated'] else "⏳ Pending"
            ev_color = "#22d3a4" if "Evaluated" in ev_status else "#f59e0b"
            funding = f"${row['target_funding']:,.0f}" if pd.notna(row['target_funding']) else "N/A"

            col_a, col_b, col_c = st.columns([4, 2, 2])
            with col_a:
                st.markdown(f"""
                <div class="startup-item" style="cursor:default;">
                  <div>
                    <div class="startup-name">{row['project_name']}</div>
                    <div class="startup-tag">{row.get('tagline','') or '—'}</div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
            with col_b:
                stage = row.get('current_stage', 'N/A') or 'N/A'
                cat = row.get('category', '') or ''
                st.markdown(f"""
                <div style="padding:0.7rem 0;font-size:0.8rem;color:#6b6b80;">
                  <div><b style="color:#a0a0b8;">Stage:</b> {stage}</div>
                  <div><b style="color:#a0a0b8;">Category:</b> {cat}</div>
                  <div><b style="color:#a0a0b8;">Funding:</b> {funding}</div>
                </div>
                """, unsafe_allow_html=True)
            with col_c:
                st.markdown(f"""
                <div style="padding:0.7rem 0;text-align:right;">
                  <div style="font-size:0.78rem;color:{ev_color};font-weight:600;">{ev_status}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("🔍 Evaluate", key=f"ev_{row['id']}"):
                    st.session_state['eval_id'] = row['id']
                    st.session_state['page_override'] = "🔍 Evaluate"
                    st.rerun()
                if st.button("🗑️", key=f"del_{row['id']}"):
                    delete_startup(row['id'])
                    st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: ADD STARTUP
# ══════════════════════════════════════════════════════════════════════════════
elif page == "➕ Add Startup":
    st.markdown('<div class="section-label">Register New Startup</div>', unsafe_allow_html=True)

    with st.form("add_startup", clear_on_submit=True):
        st.markdown("#### 🏢 Basic Information")
        c1, c2 = st.columns(2)
        with c1:
            project_name = st.text_input("Project Name *", placeholder="e.g. AgroVision AI")
            category = st.selectbox("Category", [
                "SaaS", "FinTech", "HealthTech", "EdTech", "AgriTech",
                "E-Commerce", "Marketplace", "DeepTech", "CleanTech",
                "PropTech", "LegalTech", "HRTech", "LogisticsTech",
                "Gaming", "Social", "Consumer App", "Hardware", "Other"
            ])
            team_size = st.number_input("Team Size", min_value=1, max_value=10000, value=3)
        with c2:
            tagline = st.text_input("Tagline", placeholder="One compelling sentence about what you do")
            current_stage = st.selectbox("Current Stage", [
                "Idea", "Pre-Seed", "Seed", "Series A", "Series B",
                "Series C+", "Growth", "Profitable", "Exit"
            ])
            target_funding = st.number_input("Target Funding (USD)", min_value=0.0, value=500000.0, step=50000.0)

        website_url = st.text_input("Website URL", placeholder="https://")
        current_customers = st.text_input("Current Customers / Users", placeholder="e.g. 250 paying customers, 5000 free users")

        st.markdown("#### 📝 Detailed Information")
        full_description = st.text_area("Full Description *", height=120,
            placeholder="Describe your startup in detail — what problem you solve, your solution, how it works...")
        target_market = st.text_area("Target Market", height=80,
            placeholder="Who are your customers? Market size? Demographics? Geography?")
        competition_analysis = st.text_area("Competition Analysis", height=80,
            placeholder="Who are your main competitors? What is your unique differentiation?")
        revenue_model = st.text_area("Revenue Model", height=80,
            placeholder="How do you make money? Subscription, marketplace fee, freemium, etc.?")

        st.markdown("#### 📁 Documents & Files")
        fc1, fc2 = st.columns(2)
        with fc1:
            pitch_deck = st.file_uploader("Pitch Deck (PDF/PPT)", type=["pdf", "pptx", "ppt"])
            financial_proj = st.file_uploader("Financial Projections (PDF/Excel)", type=["pdf", "xlsx", "xls"])
        with fc2:
            business_plan = st.file_uploader("Business Plan (PDF)", type=["pdf", "docx"])
            product_demo = st.file_uploader("Product Demo (PDF/Image/Video)", type=["pdf", "png", "jpg", "mp4"])

        submitted = st.form_submit_button("🚀 Register Startup", use_container_width=True)

        if submitted:
            if not project_name or not full_description:
                st.error("Please fill in Project Name and Full Description at minimum.")
            else:
                data = {
                    'project_name': project_name, 'tagline': tagline,
                    'full_description': full_description, 'category': category,
                    'target_funding': target_funding, 'website_url': website_url,
                    'team_size': team_size, 'target_market': target_market,
                    'competition_analysis': competition_analysis,
                    'revenue_model': revenue_model, 'current_stage': current_stage,
                    'current_customers': current_customers,
                    'pitch_deck': pitch_deck.read() if pitch_deck else None,
                    'pitch_deck_name': pitch_deck.name if pitch_deck else None,
                    'business_plan': business_plan.read() if business_plan else None,
                    'business_plan_name': business_plan.name if business_plan else None,
                    'financial_projections': financial_proj.read() if financial_proj else None,
                    'financial_projections_name': financial_proj.name if financial_proj else None,
                    'product_demo': product_demo.read() if product_demo else None,
                    'product_demo_name': product_demo.name if product_demo else None,
                }
                sid = save_startup(data)
                st.success(f"✅ **{project_name}** registered successfully! (ID #{sid})")
                st.balloons()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: EVALUATE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔍 Evaluate" or st.session_state.get('page_override') == "🔍 Evaluate":
    if 'page_override' in st.session_state:
        del st.session_state['page_override']

    df = get_all_startups()

    if df.empty:
        st.warning("No startups in the database yet. Add one first!")
    else:
        st.markdown('<div class="section-label">Select Startup to Evaluate</div>', unsafe_allow_html=True)

        startup_options = {f"{row['project_name']} (#{row['id']})": row['id'] for _, row in df.iterrows()}
        default_idx = 0
        if 'eval_id' in st.session_state:
            target_id = st.session_state['eval_id']
            for i, (k, v) in enumerate(startup_options.items()):
                if v == target_id:
                    default_idx = i
                    break

        selected_label = st.selectbox("Choose a startup:", list(startup_options.keys()), index=default_idx)
        selected_id = startup_options[selected_label]

        s = get_startup_by_id(selected_id)

        if s:
            # Info summary
            files = []
            if s.get('pitch_deck'):             files.append("📊 Pitch Deck")
            if s.get('business_plan'):          files.append("📄 Business Plan")
            if s.get('financial_projections'):  files.append("💹 Financials")
            if s.get('product_demo'):           files.append("🎬 Demo")

            st.markdown(f"""
            <div class="card">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:1rem;">
                <div>
                  <div style="font-family:'Syne',sans-serif;font-size:1.3rem;font-weight:800;">{s['project_name']}</div>
                  <div style="color:#6b6b80;font-size:0.85rem;margin-top:0.2rem;">{s.get('tagline') or ''}</div>
                  <div class="metric-row" style="margin-top:0.6rem;">
                    <div class="metric-pill">Stage<span>{s.get('current_stage','N/A')}</span></div>
                    <div class="metric-pill">Category<span>{s.get('category','N/A')}</span></div>
                    <div class="metric-pill">Team<span>{s.get('team_size','N/A')} people</span></div>
                    <div class="metric-pill">Funding Target<span>${s.get('target_funding',0):,.0f}</span></div>
                  </div>
                </div>
                <div style="display:flex;gap:0.4rem;flex-wrap:wrap;">
                  {''.join(f'<span style="background:#1a1a26;border:1px solid #252535;border-radius:6px;padding:0.25rem 0.6rem;font-size:0.75rem;">{f}</span>' for f in files) or '<span style="color:#3d3d50;font-size:0.8rem;">No files uploaded</span>'}
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # Show cached evaluation or run new one
            cached = s.get('evaluation_result')
            if cached:
                try:
                    ev = json.loads(cached)
                    st.markdown(f"""
                    <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:1rem;
                         padding:0.6rem 1rem;background:#0d1a0d;border:1px solid rgba(34,211,164,0.2);
                         border-radius:8px;font-size:0.82rem;color:#22d3a4;">
                      ✓ Showing cached evaluation from {s.get('last_evaluated','')[:16].replace('T',' ')}
                    </div>
                    """, unsafe_allow_html=True)
                    render_evaluation(ev)
                except Exception:
                    cached = None

            col_btn1, col_btn2 = st.columns([1, 3])
            with col_btn1:
                btn_label = "🔄 Re-Evaluate" if cached else "⚡ Run AI Evaluation"
                if st.button(btn_label, use_container_width=True):
                    with st.spinner("Analyzing startup with Mistral AI..."):
                        try:
                            ev = evaluate_startup(s)
                            update_evaluation(selected_id, json.dumps(ev))
                            st.session_state['last_eval'] = ev
                            st.rerun()
                        except json.JSONDecodeError as e:
                            st.error("AI returned invalid JSON.")
                            st.exception(e)
                        
                        except requests.exceptions.RequestException as e:
                            st.error("Could not connect to Mistral API.")
                            st.exception(e)
                        
                        except Exception as e:
                            st.exception(e)
