import streamlit as st
import json
import uuid
from datetime import datetime
from mistralai import Mistral

# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="VentureMatch — AI Startup Matching",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

:root {
    --bg: #0a0a0f;
    --surface: #12121a;
    --surface2: #1a1a26;
    --accent: #7c5cfc;
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
h1,h2,h3,h4 { font-family: 'Syne', sans-serif; }

#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

.hero {
    background: linear-gradient(135deg, #0a0a0f 0%, #1a0a2e 50%, #0a0a0f 100%);
    border-bottom: 1px solid var(--border);
    padding: 2.5rem 2rem 2rem;
    margin: -1rem -1rem 2rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content:'';position:absolute;top:-50%;left:-20%;width:60%;height:200%;
    background:radial-gradient(ellipse,rgba(124,92,252,0.12) 0%,transparent 70%);
    pointer-events:none;
}
.hero-title {
    font-family:'Syne',sans-serif;font-size:2.4rem;font-weight:800;
    background:linear-gradient(135deg,#fff 30%,#7c5cfc 70%,#fc5c7d 100%);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
    margin:0 0 0.4rem;letter-spacing:-0.03em;
}
.hero-sub { color:var(--muted);font-size:1rem;font-weight:300;letter-spacing:0.02em; }

.section-label {
    font-family:'Syne',sans-serif;font-size:0.7rem;font-weight:700;
    letter-spacing:0.12em;text-transform:uppercase;color:var(--accent);
    margin-bottom:0.75rem;display:flex;align-items:center;gap:0.5rem;
}
.section-label::after { content:'';flex:1;height:1px;background:var(--border); }

.advice-block {
    background:var(--surface2);border-left:3px solid var(--accent);
    border-radius:0 8px 8px 0;padding:1rem 1.2rem;margin-bottom:0.75rem;
    font-size:0.9rem;line-height:1.65;
}
.advice-success { border-left-color:var(--success); }
.advice-danger  { border-left-color:var(--danger); }
.advice-warning { border-left-color:var(--warning); }

.score-circle {
    width:72px;height:72px;border-radius:50%;
    display:flex;align-items:center;justify-content:center;flex-direction:column;
    background:linear-gradient(135deg,rgba(124,92,252,0.15),rgba(252,92,125,0.1));
    border:2px solid rgba(124,92,252,0.35);
}
.score-num {
    font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:800;
    background:linear-gradient(135deg,#7c5cfc,#fc5c7d);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;line-height:1;
}
.score-lbl { font-size:0.55rem;color:var(--muted);letter-spacing:0.08em;text-transform:uppercase; }

/* Streamlit overrides */
.stButton > button {
    background:linear-gradient(135deg,var(--accent),#6040e0) !important;
    color:white !important;border:none !important;border-radius:8px !important;
    font-family:'Syne',sans-serif !important;font-weight:600 !important;
    font-size:0.85rem !important;padding:0.55rem 1.4rem !important;
}
.stButton > button:hover { opacity:0.88 !important; }

.stTextInput input, .stTextArea textarea {
    background:var(--surface) !important;border:1px solid var(--border) !important;
    color:var(--text) !important;border-radius:8px !important;
}

[data-testid="stSidebar"] {
    background:var(--surface) !important;
    border-right:1px solid var(--border) !important;
}

.stTabs [data-baseweb="tab-list"] {
    background:var(--surface) !important;border-radius:8px !important;
    padding:0.2rem !important;gap:0.2rem !important;
    border:1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
    background:transparent !important;color:var(--muted) !important;
    border-radius:6px !important;font-family:'Syne',sans-serif !important;
    font-weight:600 !important;font-size:0.82rem !important;
}
.stTabs [aria-selected="true"] {
    background:var(--accent) !important;color:white !important;
}
.stExpander {
    background:var(--surface) !important;
    border:1px solid var(--border) !important;border-radius:10px !important;
}
div[data-testid="metric-container"] {
    background:var(--surface2) !important;
    border:1px solid var(--border) !important;border-radius:10px !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Mistral client — hardcoded key
# ─────────────────────────────────────────────
MISTRAL_KEY = "MpDjSDtazDWPTD1v75zLhpY77rAFF0qI"
mistral_client = Mistral(api_key=MISTRAL_KEY)

# ─────────────────────────────────────────────
# Demo data
# ─────────────────────────────────────────────
DEMO_STARTUPS = [
    {
        "id": "s1",
        "project_name": "PayFlow Africa",
        "tagline": "Instant cross-border payments for Africa",
        "full_description": "PayFlow Africa enables businesses and individuals to send money across Africa using stablecoin rails.",
        "category": "FinTech",
        "target_funding": "$2M",
        "current_stage": "Seed",
        "team_size": 8,
        "target_market": "MENA, Africa",
        "competition_analysis": "Competing with M-Pesa and WorldRemit.",
        "revenue_model": "Transaction fees",
        "current_customers": "1,200 SMEs",
        "financial_projections": "$800K ARR",
        "website_url": "",
        "pitch_deck_url": "",
        "business_plan": "Expand to 10 corridors",
        "product_demo_url": "",
        "created_at": datetime.utcnow().isoformat(),
    },
    {
        "id": "s2",
        "project_name": "MediScan AI",
        "tagline": "AI radiology for underserved hospitals",
        "full_description": "AI-powered radiology analysis for hospitals in emerging markets.",
        "category": "HealthTech",
        "target_funding": "$3M",
        "current_stage": "Series A",
        "team_size": 12,
        "target_market": "Middle East, Africa",
        "competition_analysis": "Competing with Aidoc.",
        "revenue_model": "SaaS subscription",
        "current_customers": "45 hospitals",
        "financial_projections": "$1.8M ARR",
        "website_url": "",
        "pitch_deck_url": "",
        "business_plan": "Expand globally",
        "product_demo_url": "",
        "created_at": datetime.utcnow().isoformat(),
    },
]

# ─────────────────────────────────────────────
# Session state
# ─────────────────────────────────────────────
if "startups" not in st.session_state:
    st.session_state.startups = DEMO_STARTUPS.copy()
if "match_results" not in st.session_state:
    st.session_state.match_results = None

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
CATEGORY_COLORS = {
    "FinTech": "🟦", "HealthTech": "🟥", "EdTech": "🟨",
    "AgriTech": "🟩", "CleanTech": "🟦", "Logistics": "🟪",
    "SaaS": "🔵", "E-Commerce": "🟠", "AI/ML": "⚪", "Other": "⚫",
}

def get_categories():
    return sorted(set(s["category"] for s in st.session_state.startups))

def score_bar_html(value):
    pct = value
    color = "#22d3a4" if pct >= 70 else "#f59e0b" if pct >= 40 else "#ef4444"
    return f"""
    <div style="margin:0.5rem 0 0.8rem;">
      <div style="display:flex;justify-content:space-between;margin-bottom:0.25rem;">
        <span style="font-size:0.78rem;color:#a0a0b8;">Match Score</span>
        <span style="font-size:0.78rem;font-weight:700;color:{color};">{value}/100</span>
      </div>
      <div style="height:5px;background:#1a1a26;border-radius:99px;overflow:hidden;">
        <div style="height:100%;width:{pct}%;background:{color};border-radius:99px;"></div>
      </div>
    </div>"""

# ─────────────────────────────────────────────
# AI Matching — mistralai SDK (same as startup evaluator)
# ─────────────────────────────────────────────
def run_ai_match(investor: dict, top_k: int) -> dict:
    summaries = []
    for i, s in enumerate(st.session_state.startups):
        summaries.append(f"""
[{i+1}] ID: {s['id']} | Name: {s['project_name']}
Category: {s['category']} | Stage: {s['current_stage']} | Funding: {s['target_funding']}
Team: {s['team_size']} | Market: {s['target_market']} | Revenue: {s['revenue_model']}
Customers: {s.get('current_customers','N/A')} | Financials: {s.get('financial_projections','N/A')}
Description: {s['full_description']}
Competition: {s.get('competition_analysis','N/A')}
""")

    prompt = f"""You are a senior VC investment analyst. Analyze the startups below and recommend the BEST {top_k} matches for this investor.

INVESTOR PROFILE:
Name: {investor['name']}
Investment Focus: {investor['focus']}
Preferred Stage: {investor['stage']}
Ticket Size: {investor['ticket']}
Preferred Markets: {investor.get('markets', 'Any')}
Risk Appetite: {investor.get('risk', 'Medium')}
Sectors to Avoid: {investor.get('avoid', 'None')}
Notes: {investor.get('notes', 'None')}

STARTUPS:
{''.join(summaries)}

Return ONLY valid JSON (no markdown, no backticks) with this exact structure:
{{
  "matches": [
    {{
      "startup_id": "id",
      "startup_name": "name",
      "match_score": 90,
      "match_summary": "2-sentence summary of why this is a fit",
      "key_strengths": ["strength 1", "strength 2", "strength 3"],
      "key_risks": ["risk 1", "risk 2"],
      "recommendation": "Specific actionable recommendation for the investor"
    }}
  ],
  "overall_analysis": "1-paragraph portfolio-level analysis of the matches"
}}"""

    response = mistral_client.chat.complete(
        model="mistral-large-latest",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2000,
    )

    raw = response.choices[0].message.content.strip()
    # Strip accidental markdown fences
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())

# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-title">VentureMatch AI</div>
  <div class="hero-sub">AI-powered startup–investor matching powered by Mistral Large</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:700;
         margin-bottom:1.2rem;color:#e8e8f0;">📊 Database Stats</div>
    """, unsafe_allow_html=True)

    startups = st.session_state.startups
    c1, c2 = st.columns(2)
    c1.metric("Startups", len(startups))
    c2.metric("Categories", len(get_categories()))
    avg_team = sum(s["team_size"] for s in startups) // max(len(startups), 1)
    c1.metric("Avg Team Size", avg_team)
    c2.metric("Unique Stages", len(set(s["current_stage"] for s in startups)))

    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.72rem;color:#3d3d50;line-height:1.7;">
    🔑 API key pre-configured<br>
    Powered by Mistral Large<br>
    Fill investor profile → get<br>AI-ranked startup matches.
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Tabs
# ─────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📋 Database", "➕ Add Startup", "🤖 AI Match"])

# ══════════════════════════════
# TAB 1 — Startup Database
# ══════════════════════════════
with tab1:
    st.markdown('<div class="section-label">Startup Registry</div>', unsafe_allow_html=True)

    if not st.session_state.startups:
        st.info("No startups yet. Add one in the next tab.")
    else:
        for s in st.session_state.startups:
            icon = CATEGORY_COLORS.get(s["category"], "⚫")
            with st.expander(f"{icon} **{s['project_name']}** — {s['current_stage']} · {s['category']}"):
                c1, c2, c3 = st.columns(3)
                c1.markdown(f"**Funding:** {s['target_funding']}")
                c1.markdown(f"**Stage:** {s['current_stage']}")
                c2.markdown(f"**Team:** {s['team_size']} people")
                c2.markdown(f"**Market:** {s['target_market']}")
                c3.markdown(f"**Customers:** {s.get('current_customers','N/A')}")
                c3.markdown(f"**Financials:** {s.get('financial_projections','N/A')}")

                st.markdown(f"*{s['tagline']}*")
                st.write(s["full_description"])

                ca, cb = st.columns(2)
                with ca:
                    st.markdown("**Revenue Model**")
                    st.markdown(f'<div class="advice-block">{s["revenue_model"]}</div>', unsafe_allow_html=True)
                with cb:
                    st.markdown("**Competition**")
                    st.markdown(f'<div class="advice-block advice-warning">{s.get("competition_analysis","N/A")}</div>', unsafe_allow_html=True)

# ══════════════════════════════
# TAB 2 — Add Startup
# ══════════════════════════════
with tab2:
    st.markdown('<div class="section-label">Register New Startup</div>', unsafe_allow_html=True)

    with st.form("startup_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        project_name = c1.text_input("Project Name *")
        category = c2.selectbox("Category *", [
            "", "FinTech", "HealthTech", "EdTech", "AgriTech",
            "CleanTech", "Logistics", "SaaS", "E-Commerce", "AI/ML", "Other"
        ])

        tagline = st.text_input("Tagline *", placeholder="One compelling sentence about what you do")
        full_description = st.text_area("Full Description *", height=110)

        c3, c4 = st.columns(2)
        target_funding = c3.text_input("Target Funding *", placeholder="e.g. $2M")
        current_stage = c4.selectbox("Current Stage *", [
            "", "Idea", "Pre-Seed", "Seed", "Series A", "Series B", "Profitable"
        ])

        c5, c6 = st.columns(2)
        team_size = c5.number_input("Team Size", min_value=1, value=5)
        target_market = c6.text_input("Target Market *")

        c7, c8 = st.columns(2)
        revenue_model = c7.text_input("Revenue Model *")
        current_customers = c8.text_input("Current Customers")

        c9, c10 = st.columns(2)
        financial_projections = c9.text_input("Financial Projections")
        website_url = c10.text_input("Website URL")

        competition_analysis = st.text_area("Competition Analysis", height=80)

        submitted = st.form_submit_button("✅ Add Startup", use_container_width=True)

        if submitted:
            required = [project_name, category, tagline, full_description, target_funding, current_stage, target_market, revenue_model]
            if not all(required):
                st.error("Please fill all required (*) fields.")
            else:
                st.session_state.startups.append({
                    "id": str(uuid.uuid4()),
                    "project_name": project_name,
                    "tagline": tagline,
                    "full_description": full_description,
                    "category": category,
                    "target_funding": target_funding,
                    "current_stage": current_stage,
                    "team_size": int(team_size),
                    "target_market": target_market,
                    "revenue_model": revenue_model,
                    "competition_analysis": competition_analysis,
                    "current_customers": current_customers,
                    "financial_projections": financial_projections,
                    "website_url": website_url,
                    "pitch_deck_url": "",
                    "business_plan": "",
                    "product_demo_url": "",
                    "created_at": datetime.utcnow().isoformat(),
                })
                st.success(f"✅ **{project_name}** added successfully!")
                st.balloons()

# ══════════════════════════════
# TAB 3 — AI Match
# ══════════════════════════════
with tab3:
    st.markdown('<div class="section-label">Investor Profile</div>', unsafe_allow_html=True)

    with st.form("investor_form"):
        c1, c2 = st.columns(2)
        investor_name    = c1.text_input("Investor / Fund Name *")
        investment_focus = c2.text_input("Investment Focus *", placeholder="e.g. FinTech, AI, SaaS")

        c3, c4 = st.columns(2)
        investment_stage = c3.selectbox("Preferred Stage *", [
            "", "Pre-Seed", "Seed", "Series A", "Series B", "Any Stage"
        ])
        ticket_size = c4.text_input("Ticket Size *", placeholder="e.g. $500K – $2M")

        c5, c6 = st.columns(2)
        preferred_markets = c5.text_input("Preferred Markets", placeholder="e.g. MENA, Africa")
        risk_appetite     = c6.selectbox("Risk Appetite", ["Low", "Medium", "High"])

        c7, c8 = st.columns(2)
        sectors_avoid = c7.text_input("Sectors to Avoid")
        top_k         = c8.selectbox("Number of Matches", [3, 4, 5], index=2)

        additional_notes = st.text_area("Additional Notes / Investment Thesis", height=80)

        submit_match = st.form_submit_button("🚀 Find Matches", use_container_width=True, type="primary")

    if submit_match:
        if not all([investor_name, investment_focus, investment_stage, ticket_size]):
            st.error("Please fill all required (*) fields.")
        else:
            investor = {
                "name": investor_name, "focus": investment_focus,
                "stage": investment_stage, "ticket": ticket_size,
                "markets": preferred_markets, "risk": risk_appetite,
                "avoid": sectors_avoid, "notes": additional_notes,
            }
            with st.spinner("Analyzing startups with Mistral AI…"):
                try:
                    result = run_ai_match(investor, top_k)
                    st.session_state.match_results = result
                except json.JSONDecodeError as e:
                    st.error(f"Could not parse AI response — please try again. ({e})")
                except Exception as e:
                    st.error(f"Error: {e}")

    # ── Results ──────────────────────────────────────────────
    if st.session_state.match_results:
        data = st.session_state.match_results
        st.markdown('<div class="section-label" style="margin-top:1.5rem;">Match Results</div>', unsafe_allow_html=True)

        if data.get("overall_analysis"):
            st.markdown(f"""
            <div style="background:#12121a;border:1px solid rgba(124,92,252,0.25);border-radius:10px;
                 padding:1.2rem 1.4rem;margin-bottom:1.5rem;font-size:0.88rem;line-height:1.65;
                 color:#c8c8e0;font-style:italic;">
              📊 {data['overall_analysis']}
            </div>
            """, unsafe_allow_html=True)

        medals = ["🥇", "🥈", "🥉"]
        for i, m in enumerate(data.get("matches", [])):
            score  = m.get("match_score", 0)
            badge  = medals[i] if i < 3 else f"#{i+1}"
            s_color = "#22d3a4" if score >= 70 else "#f59e0b" if score >= 40 else "#ef4444"

            with st.expander(f"{badge} **{m['startup_name']}** — {score}/100", expanded=(i == 0)):
                col_score, col_info = st.columns([1, 4])
                with col_score:
                    st.markdown(f"""
                    <div class="score-circle" style="margin:0.5rem auto;">
                      <div class="score-num" style="-webkit-text-fill-color:{s_color} !important;">{score}</div>
                      <div class="score-lbl">/ 100</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_info:
                    st.markdown(f"**{m.get('match_summary','')}**")
                    st.markdown(score_bar_html(score), unsafe_allow_html=True)

                c_str, c_risk = st.columns(2)
                with c_str:
                    st.markdown('<div class="section-label" style="margin-top:0.8rem;">Strengths</div>', unsafe_allow_html=True)
                    for strength in m.get("key_strengths", []):
                        st.markdown(f'<div class="advice-block advice-success">✦ {strength}</div>', unsafe_allow_html=True)
                with c_risk:
                    st.markdown('<div class="section-label" style="margin-top:0.8rem;">Risks</div>', unsafe_allow_html=True)
                    for risk in m.get("key_risks", []):
                        st.markdown(f'<div class="advice-block advice-danger">◇ {risk}</div>', unsafe_allow_html=True)

                st.markdown(f"""
                <div style="background:linear-gradient(135deg,#12121a,#1a1226);
                     border:1px solid rgba(124,92,252,0.25);border-radius:10px;
                     padding:1rem 1.2rem;margin-top:0.5rem;font-size:0.88rem;line-height:1.65;">
                  <span style="font-family:'Syne',sans-serif;font-weight:700;color:#7c5cfc;">
                    💡 Recommendation
                  </span><br>
                  <span style="color:#c8c8e0;">{m.get('recommendation','')}</span>
                </div>
                """, unsafe_allow_html=True)

        st.download_button(
            label="⬇️ Export Results as JSON",
            data=json.dumps(data, indent=2),
            file_name="venture_matches.json",
            mime="application/json",
            use_container_width=True,
        )
