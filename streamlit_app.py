import json
import time
import os
from datetime import datetime
from collections import Counter
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import threading
import schedule
from scraper import SOURCES, scrape_all, search_headlines, cluster_headlines
from mailer import send_news_digest

# --- Page Configuration ---
st.set_page_config(
    page_title="Global News Scraper | Live", 
    page_icon="📡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Enhanced Professional UI Styling ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@600;700;800&family=JetBrains+Mono:wght@500&display=swap');

    /* Professional Base */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        font-family: 'Inter', sans-serif;
        background-color: #0f172a !important; /* Deep Navy Slate */
        color: #f1f5f9 !important;
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #0f172a; }
    ::-webkit-scrollbar-thumb { background: #334155; border-radius: 10px; }

    /* Sidebar - Professional Drawer */
    [data-testid="stSidebar"] {
        background-color: #1e293b !important;
        border-right: 1px solid #334155;
    }
    
    [data-testid="stSidebar"] h1 {
        font-family: 'Outfit', sans-serif;
        font-size: 1.5rem !important;
        color: #38bdf8 !important;
        font-weight: 700;
        margin-bottom: 2rem !important;
    }

    /* Dashboard Header */
    .dashboard-header {
        background: #1e293b;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        border: 1px solid #334155;
        margin-bottom: 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    .header-title-section h1 {
        font-family: 'Outfit', sans-serif;
        font-size: 2rem !important;
        margin: 0 !important;
        color: #f8fafc;
        letter-spacing: -0.02em;
    }
    
    .header-subtitle {
        color: #94a3b8;
        font-size: 0.9rem;
        margin-top: 0.25rem;
    }

    /* Professional News Card */
    .news-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.25rem;
        transition: all 0.2s ease-in-out;
        display: flex;
        flex-direction: column;
        height: 100%;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    .news-card:hover {
        border-color: #38bdf8;
        background: #243146;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
    }

    .source-label {
        font-family: 'JetBrains Mono', monospace;
        color: #38bdf8;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 0.75rem;
        display: block;
    }

    .news-title {
        font-size: 1.15rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
        color: #f1f5f9;
        line-height: 1.4;
    }

    .news-summary {
        font-size: 0.9rem;
        color: #94a3b8;
        margin-bottom: 1.25rem;
        line-height: 1.5;
        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }

    /* Metadata Chips */
    .meta-chip {
        display: inline-flex;
        align-items: center;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 600;
        margin-right: 6px;
        background: #0f172a;
        border: 1px solid #334155;
    }

    .sentiment-indicator {
        width: 8px; height: 8px;
        border-radius: 50%;
        margin-right: 6px;
    }
    .sent-pos { background: #10b981; }
    .sent-neg { background: #ef4444; }
    .sent-neu { background: #64748b; }

    /* Action Footer */
    .card-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: auto;
        padding-top: 1rem;
        border-top: 1px solid #334155;
    }

    .timestamp {
        font-size: 0.75rem;
        color: #64748b;
    }

    .action-link {
        color: #38bdf8;
        text-decoration: none;
        font-weight: 600;
        font-size: 0.8rem;
    }

    /* Stats Badge */
    .stat-badge {
        background: #0f172a;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        border: 1px solid #334155;
        font-size: 0.85rem;
        color: #cbd5e1;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* Tabs Override */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        border-bottom: 1px solid #334155;
    }
    .stTabs [data-baseweb="tab"] {
        color: #94a3b8;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        border-radius: 8px 8px 0 0;
    }
    .stTabs [aria-selected="true"] {
        color: #38bdf8 !important;
        background: #1e293b !important;
        border-bottom: 2px solid #38bdf8 !important;
    }

    /* Buttons */
    .stButton>button {
        background: #38bdf8;
        color: #0f172a;
        border: none;
        font-weight: 700;
        border-radius: 6px;
    }
    .stButton>button:hover {
        background: #7dd3fc;
        color: #0f172a;
    }

    /* News Ticker */
    .ticker-wrap {
        width: 100%;
        overflow: hidden;
        background-color: #0f172a;
        padding: 10px 0;
        border-bottom: 1px solid #334155;
        position: sticky;
        top: 0;
        z-index: 999;
    }
    .ticker {
        display: inline-block;
        white-space: nowrap;
        padding-right: 100%;
        animation: ticker 60s linear infinite;
    }
    .ticker__item {
        display: inline-block;
        padding: 0 2rem;
        font-size: 0.85rem;
        color: #38bdf8;
        font-weight: 500;
        border-right: 1px solid #334155;
    }
    @keyframes ticker {
        0% { transform: translate3d(0, 0, 0); }
        100% { transform: translate3d(-100%, 0, 0); }
    }

    /* Sidebar Refinements */
    .sidebar-section {
        background: #0f172a;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border: 1px solid #334155;
    }
    .status-dot {
        height: 8px; width: 8px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
    }
    .status-online { background: #10b981; box-shadow: 0 0 5px #10b981; }
    </style>
""", unsafe_allow_html=True)

# --- Data Persistence (Bookmarks, Users, Config) ---
BOOKMARKS_FILE = "bookmarks.json"
USERS_FILE = "users.json"
CONFIG_FILE = "config.json"

if "bookmarks" not in st.session_state:
    if os.path.exists(BOOKMARKS_FILE):
        with open(BOOKMARKS_FILE, "r") as f:
            st.session_state.bookmarks = json.load(f)
    else:
        st.session_state.bookmarks = []

if "users" not in st.session_state:
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            st.session_state.users = json.load(f)
    else:
        st.session_state.users = []

if "config" not in st.session_state:
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            st.session_state.config = json.load(f)
    else:
        st.session_state.config = {"smtp_email": "", "smtp_pass": ""}

def save_config(email, password):
    st.session_state.config = {"smtp_email": email, "smtp_pass": password}
    with open(CONFIG_FILE, "w") as f:
        json.dump(st.session_state.config, f)
    st.toast("⚙️ Configuration Saved!")

def save_bookmark(item):
    if item not in st.session_state.bookmarks:
        st.session_state.bookmarks.append(item)
        with open(BOOKMARKS_FILE, "w") as f:
            json.dump(st.session_state.bookmarks, f)
        st.toast("✅ Bookmarked!")


def check_login(email, password):
    for u in st.session_state.users:
        if u['email'] == email and u.get('password', '') == password:
            return True, u
    return False, None

def register_user(name, email, password):
    user_data = {"name": name, "email": email, "password": password, "joined": datetime.now().isoformat()}
    if not any(u['email'] == email for u in st.session_state.users):
        st.session_state.users.append(user_data)
        with open(USERS_FILE, "w") as f:
            json.dump(st.session_state.users, f)
        return True
    return False

def run_bg_automation():
    """Background task to run schedule in a separate thread."""
    while True:
        schedule.run_pending()
        time.sleep(60)

def auto_delivery_task():
    """Logic to send daily digest automatically."""
    if os.path.exists(CONFIG_FILE) and os.path.exists(USERS_FILE):
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
        with open(USERS_FILE, "r") as f:
            users = json.load(f)
            
        if config.get("smtp_email") and config.get("smtp_pass") and users:
            headlines = scrape_all(verbose=False)
            df_temp = pd.DataFrame(headlines)
            df_temp['impact'] = df_temp['polarity'].abs()
            moti_news = df_temp.sort_values('impact', ascending=False).head(10)
            news_list = list(moti_news.itertuples())
            
            for user in users:
                send_news_digest(config["smtp_email"], config["smtp_pass"], user["email"], news_list)

# Start background thread only once
if "scheduler_started" not in st.session_state:
    schedule.every().day.at("10:00").do(auto_delivery_task)
    # Also for testing/demonstration, you can add: schedule.every(1).hours.do(auto_delivery_task)
    thread = threading.Thread(target=run_bg_automation, daemon=True)
    thread.start()
    st.session_state.scheduler_started = True

def generate_bot_response(query, headlines):
    import re
    query_lower = query.lower().strip()
    
    if not headlines:
        return "I don't have any news headlines currently cached. Please click **Manual Sync Now** in the sidebar to scrape the latest headlines!"
        
    if any(g in query_lower for g in ["hello", "hi", "hey", "hola", "yo", "greeting"]):
        return "Hello! I am your Global News Intelligence assistant. How can I help you analyze the news today? You can ask me to summarize news from a specific channel (e.g. *'Show BBC'*), check sentiment (*'Find positive stories'*), or search for any keyword (*'Latest on China'*)."
        
    matched_source = None
    for src in SOURCES.keys():
        if src.lower() in query_lower:
            matched_source = src
            break
    
    requested_sentiment = None
    if "positive" in query_lower:
        requested_sentiment = "Positive"
    elif "negative" in query_lower:
        requested_sentiment = "Negative"
    elif "neutral" in query_lower:
        requested_sentiment = "Neutral"

    filtered = headlines
    if matched_source:
        filtered = [h for h in filtered if h["source"] == matched_source]
        
    if requested_sentiment:
        filtered = [h for h in filtered if h.get("sentiment") == requested_sentiment]
        
    clean_query = query_lower
    for word in ["show", "me", "find", "search", "about", "latest", "news", "stories", "headlines", "on", "tell", "regarding", "what is", "what are", "the", "for"]:
        clean_query = re.sub(rf"\b{word}\b", "", clean_query)
    clean_query = re.sub(r"[^\w\s]", "", clean_query).strip()
    
    if clean_query and not matched_source and not requested_sentiment:
        filtered = search_headlines(headlines, clean_query)
        if not filtered:
            words = [w for w in clean_query.split() if len(w) > 2]
            if words:
                filtered = [h for h in headlines if any(w in (h["title"] + " " + h["description"]).lower() for w in words)]

    if not filtered:
        return f"I couldn't find any articles matching your query *'{query}'*. Try searching for other terms like *'US'*, *'Crypto'*, or specify a channel like *'BBC News'*!"

    df_filtered = pd.DataFrame(filtered)
    avg_polarity = df_filtered['polarity'].mean() if 'polarity' in df_filtered.columns else 0.0
    sentiment_summary = "Positive 🟢" if avg_polarity > 0.1 else "Negative 🔴" if avg_polarity < -0.1 else "Neutral 🟡"
    
    response = f"### 📊 Intelligence Summary for: *{query}*\n"
    response += f"- **Reports found:** {len(filtered)}\n"
    response += f"- **Average Sentiment:** {sentiment_summary} (Polarity: {avg_polarity:.2f})\n\n"
    response += "Here are the top matching intelligence updates:\n\n"
    
    for idx, item in enumerate(filtered[:5], 1):
        desc = item.get("description", "")
        if desc == "N/A" or len(desc) < 10:
            desc = "Full report details available at the source link."
        response += f"**{idx}. [{item['title']}]({item['link']})** ({item['source']})\n"
        response += f"> {desc[:140]}...\n"
        response += f"> *Published: {item['published'][:16]}* | [Open Article]({item['link']})\n\n"
        
    return response




# --- Auth Flow ---
if not st.session_state.get("logged_in", False):
    st.markdown("<h1 style='text-align: center; color: #38bdf8;'>Global News Intelligence</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8;'>Sign in or create an account to access the dashboard and receive daily intel.</p>", unsafe_allow_html=True)
    
    auth_tabs = st.tabs(["🔒 Login", "📝 Sign Up"])
    
    with auth_tabs[0]:
        with st.form("login_form"):
            st.subheader("Login to your account")
            email = st.text_input("Email Address")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign In", use_container_width=True)
            if submitted:
                success, user = check_login(email, password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.current_user = user
                    st.rerun()
                else:
                    st.error("Invalid email or password.")
                    
    with auth_tabs[1]:
        with st.form("signup_form"):
            st.subheader("Create a new account")
            new_name = st.text_input("Full Name")
            new_email = st.text_input("Email Address")
            new_password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Register & Subscribe", use_container_width=True)
            if submitted:
                if new_name and "@" in new_email and new_password:
                    if register_user(new_name, new_email, new_password):
                        st.success(f"Success! {new_name}, your account is created. Please log in.")
                        st.balloons()
                    else:
                        st.warning("This email is already registered.")
                else:
                    st.error("Please fill all fields correctly.")
                    
    st.stop()

# --- App Logic ---
if "headlines" not in st.session_state:
    st.session_state.headlines = scrape_all(verbose=False)
    st.session_state.last_refresh = datetime.now().strftime("%I:%M:%S %p")

# --- News Ticker ---
ticker_items = "".join([f'<div class="ticker__item">🚀 {h["title"]} ({h["source"]})</div>' for h in st.session_state.headlines[:10]])
st.markdown(f'<div class="ticker-wrap"><div class="ticker">{ticker_items}</div></div>', unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.markdown("<h1>Intelligence Hub</h1>", unsafe_allow_html=True)
    st.markdown(f"**Welcome, {st.session_state.current_user['name']}**")
    if st.button("Log Out", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
    st.divider()

    
    # Auto-Refresh Toggle
    st.markdown("### ⚡ Live Sync Settings")
    auto_refresh = st.toggle("Enable Live Mode (Auto-Sync)", value=False)
    refresh_interval = st.slider("Sync Interval (Seconds)", min_value=30, max_value=300, value=60, step=30)
    
    if st.button("🔄 Manual Sync Now", use_container_width=True, type="primary"):
        with st.spinner("Synchronizing feeds..."):
            st.session_state.headlines = scrape_all(verbose=False)
        st.session_state.last_refresh = datetime.now().strftime("%I:%M:%S %p")
        st.rerun()

    st.markdown("### 🌐 Data Configuration")
    source_choice = st.selectbox("Channel selection", ["All Global Channels"] + list(SOURCES.keys()))
    
    st.markdown("### ⚖️ Intelligence Filters")
    sentiment_filter = st.multiselect("Sentiment analysis", ["Positive", "Neutral", "Negative"], default=["Positive", "Neutral", "Negative"])
    
    st.markdown("### 🔍 Advanced Search")
    keyword = st.text_input("Deep search keyword", placeholder="e.g. Gaza, /crypto.*/").strip()
    
    st.divider()
    st.markdown("### 📡 Channel Health")
    for src in list(SOURCES.keys())[:5]:
        st.markdown(f'<div class="sidebar-section"><span class="status-dot status-online"></span>{src}</div>', unsafe_allow_html=True)
    
    if keyword or source_choice != "All Global Channels":
        if st.button("Clear All Filters", use_container_width=True):
            st.rerun()

    st.divider()
    st.markdown(f"**Sync Status:** {'🟢 Live' if auto_refresh else '⚪ Manual'}")
    st.markdown(f"**Last Data Burst:** {st.session_state.last_refresh}")
    
    # Export
    csv_data = "source,title,link,published\n" + "\n".join([f'"{h["source"]}","{h["title"]}","{h["link"]}","{h["published"]}"' for h in st.session_state.headlines])
    st.download_button("📥 Export Intelligence (CSV)", csv_data, "global_intel.csv", "text/csv", use_container_width=True)

# --- Main Content ---
st.markdown(f"""
<div class="dashboard-header">
<div class="header-title-section">
<h1>Global News Intelligence</h1>
<div class="header-subtitle">
Monitoring {len(SOURCES)} global channels with real-time AI sentiment analysis
{" • <span class='live-dot'></span><span style='color:#10b981; font-weight:600;'>LIVE SYNC ACTIVE</span>" if auto_refresh else ""}
</div>
</div>
<div style="display: flex; gap: 1rem;">
<div class="stat-badge"><span>📊</span> {len(st.session_state.headlines)} Reports</div>
<div class="stat-badge"><span>🕒</span> {st.session_state.last_refresh}</div>
</div>
</div>
""", unsafe_allow_html=True)

# --- Main App Tabs ---
tabs = st.tabs(["🌍 Global Stories", "🚀 Live Intelligence Feed", "📊 Analytics & Trends", "💬 Intel Chatbot", "🔖 Bookmarks", "👤 Profile"])
tab0, tab1, tab2, tab3, tab4, tab5 = tabs[0], tabs[1], tabs[2], tabs[3], tabs[4], tabs[5]

with tab0:
    # Top Intelligence Summary
    if st.session_state.headlines:
        st.markdown("""
<div style="background: rgba(56, 189, 248, 0.05); border: 1px dashed #38bdf8; padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem;">
<h4 style="margin: 0 0 1rem 0; color: #38bdf8;">🧠 Top Intelligence Highlights</h4>
<div style="display: flex; flex-direction: column; gap: 0.75rem;">
<div>• <b>Major Coverage:</b> Most discussed topics involve <i>{}</i>.</div>
<div>• <b>Sentiment Shift:</b> The overall mood of current reporting is <i>{}</i>.</div>
<div>• <b>Source Diversity:</b> Information is being cross-verified across <i>{}</i> active channels.</div>
</div>
</div>
""".format(
            ", ".join([e for h in st.session_state.headlines for e in h.get('entities', [])][:3]),
            "Positive" if pd.DataFrame(st.session_state.headlines)['polarity'].mean() > 0 else "Neutral/Negative",
            len(set(h['source'] for h in st.session_state.headlines))
        ), unsafe_allow_html=True)

    st.markdown("### 🧬 Clustered Global Intelligence")
    st.caption("Headlines from different sources grouped into single unified stories.")
    
    if st.session_state.headlines:
        clusters = cluster_headlines(st.session_state.headlines)
        
        for idx, cluster in enumerate(clusters[:15]):
            with st.container():
                # Confidence Color
                conf_color = "#10b981" if cluster["confidence_score"] > 70 else "#f59e0b" if cluster["confidence_score"] > 40 else "#ef4444"
                
                st.markdown(f"""
<div class="news-card" style="border-left: 3px solid {conf_color};">
<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
<span class="source-label">Cluster Analysis #{idx+1}</span>
<span class="meta-chip">{cluster['confidence_score']}% Match</span>
</div>
<div class="news-title">{cluster['main_title']}</div>
<div style="display: flex; gap: 8px; margin-bottom: 1rem;">
<span class="meta-chip">📡 {cluster['source_count']} Sources</span>
<span class="meta-chip">📄 {cluster['coverage_count']} Articles</span>
</div>
<div class="timestamp">Latest Activity: {cluster['latest_update'][:20]}</div>
</div>
""", unsafe_allow_html=True)
                
                with st.expander("🔍 View Cross-Source Coverage & Timeline"):
                    c1, c2 = st.columns([1, 1])
                    for a_idx, art in enumerate(cluster["articles"]):
                        col = c1 if a_idx % 2 == 0 else c2
                        with col:
                            st.markdown(f"""
                                <div style="background: rgba(255,255,255,0.03); padding: 12px; border-radius: 6px; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.05);">
                                    <strong style="color: #60a5fa; font-size: 0.8rem;">{art['source']}</strong><br>
                                    <span style="font-size: 0.85rem; color: #ffffff;">{art['title']}</span>
                                    <div style="text-align: right; margin-top: 5px;">
                                        <a href="{art['link']}" target="_blank" style="font-size: 0.75rem; color: #3b82f6; text-decoration: none;">View Original →</a>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                st.divider()
    else:
        st.info("Gathering stories... Please sync if empty.")

with tab1:
    # Auto-Refresh Logic
    if auto_refresh:
        st.caption(f"Next sync in {refresh_interval} seconds...")
        st.markdown(f"""
            <script>
                setTimeout(function(){{
                    window.location.reload();
                }}, {refresh_interval * 1000});
            </script>
        """, unsafe_allow_html=True)

    # Filtering Logic
    headlines = st.session_state.headlines
    if source_choice != "All Global Channels":
        headlines = [h for h in headlines if h["source"] == source_choice]
    
    # Filter by sentiment
    headlines = [h for h in headlines if h.get("sentiment") in sentiment_filter]
    
    if keyword:
        headlines = search_headlines(headlines, keyword)

    # Stats Row
    # Stats line removed as it's now in the header
    pass

    # Content Grid
    if headlines:
        cols = st.columns(3)
        for idx, item in enumerate(headlines):
            col_idx = idx % 3
            with cols[col_idx]:
                sent_class = f"sent-{item.get('sentiment', 'neutral').lower()}"
                entities_html = "".join([f'<span class="entity-tag">{e}</span>' for e in item.get('entities', [])[:3]])
                
                desc = item.get("description", "Access the full story via the source link.")
                if len(desc) < 20: desc = "Full report available on source website."
                
                st.markdown(f"""
<div class="news-card">
<span class="source-label">{item['source']}</span>
<div class="news-title">{item['title']}</div>
<div class="news-summary">{desc[:140]}...</div>
<div style="margin-bottom: 1rem; display: flex; flex-wrap: wrap; gap: 6px;">
<div class="meta-chip">
<span class="sentiment-indicator { 'sent-pos' if item.get('sentiment') == 'Positive' else 'sent-neg' if item.get('sentiment') == 'Negative' else 'sent-neu' }"></span>
{item.get('sentiment', 'Neutral')}
</div>
{' '.join([f'<div class="meta-chip">{e}</div>' for e in item.get('entities', [])[:2]])}
</div>
<div class="card-footer">
<span class="timestamp">{item['published'][:16]}</span>
<a href="{item['link']}" target="_blank" class="action-link">Open Report →</a>
</div>
</div>
""", unsafe_allow_html=True)
                if st.button(f"🔖 Bookmark", key=f"bk_{idx}_{item['title'][:10]}"):
                    save_bookmark(item)
    else:
        st.error(f"Zero reports found for: '{keyword}'")

with tab2:
    st.markdown("### 📈 Real-time Analytics Dashboard")
    if st.session_state.headlines:
        df = pd.DataFrame(st.session_state.headlines)
        
        c1, c2 = st.columns(2)
        
        with c1:
            # Sentiment Distribution
            fig_sent = px.pie(df, names='sentiment', title='Global Sentiment Split',
                             color_discrete_map={'Positive':'#10b981', 'Negative':'#ef4444', 'Neutral':'#6b7280'},
                             hole=0.4)
            fig_sent.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
            st.plotly_chart(fig_sent, use_container_width=True)
            
        with c2:
            # Source Volume
            source_counts = df['source'].value_counts().reset_index()
            fig_vol = px.bar(source_counts, x='count', y='source', orientation='h', 
                             title='Coverage Volume by Channel',
                             color='count', color_continuous_scale='Blues')
            fig_vol.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
            st.plotly_chart(fig_vol, use_container_width=True)

        # Sentiment Trend over Time
        st.markdown("### 📈 Sentiment Velocity")
        df['dt'] = pd.to_datetime(df['timestamp'], format='ISO8601', utc=True)
        df_trend = df.sort_values('dt').groupby(df['dt'].dt.floor('h'))['polarity'].mean().reset_index()
        fig_trend = px.line(df_trend, x='dt', y='polarity', title='Global Sentiment Pulse (Hourly)',
                           line_shape='spline', render_mode='svg')
        fig_trend.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white',
                               xaxis_title="Time (UTC)", yaxis_title="Avg Polarity (-1 to 1)")
        fig_trend.update_traces(line_color='#38bdf8', line_width=3)
        st.plotly_chart(fig_trend, use_container_width=True)

        # Keyword Cloud (Simple Table)
        st.markdown("### 🔑 Top Intelligence Entities")
        all_entities = [e for h in st.session_state.headlines for e in h.get('entities', [])]
        ent_counts = Counter(all_entities).most_common(10)
        ent_df = pd.DataFrame(ent_counts, columns=['Entity', 'Mentions'])
        st.table(ent_df)
    else:
        st.info("Analytics will be available once data is fetched.")

with tab3:
    st.markdown("### 💬 News Intelligence Assistant")
    st.caption("Ask questions about the current news, analyze sentiment, or filter topics.")
    
    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "content": "Hello! I am your Global News Intelligence assistant. Ask me anything about the current headlines!"}
        ]
        
    # Quick suggestion chips
    st.markdown("**Suggestions:**")
    cols = st.columns(4)
    suggestions = [
        "Summarize BBC News",
        "Show positive stories",
        "Search news on Technology",
        "Compare Dawn vs Reuters"
    ]
    
    selected_suggestion = None
    for idx, sug in enumerate(suggestions):
        with cols[idx % 4]:
            if st.button(sug, key=f"sug_{idx}", use_container_width=True):
                selected_suggestion = sug
                
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    # User Input
    user_input = st.chat_input("Ask a question about today's news headlines...")
    
    # Handle user interaction
    query = user_input or selected_suggestion
    if query:
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": query})
        
        # Generate bot response
        response = generate_bot_response(query, st.session_state.headlines)
        
        # Add bot response to history
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()

with tab4:
    st.markdown("### 🔖 Your Saved Intelligence")
    if st.session_state.bookmarks:
        for b in st.session_state.bookmarks:
            with st.expander(f"📌 {b['title']} ({b['source']})"):
                st.write(f"**Source:** {b['source']} | **Date:** {b['published']}")
                st.write(b['description'])
                st.link_button("View Full Report", b['link'])
    else:
        st.info("No bookmarks saved yet. Click the 🔖 button on any news card to save it.")

with tab5:
    st.markdown("### 👤 Member Profile")
    st.write(f"**Name:** {st.session_state.current_user['name']}")
    st.write(f"**Email:** {st.session_state.current_user['email']}")
    st.success("✅ You are subscribed to the daily Top 10 Intelligence digest at 10:00 AM.")



# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center; color: #475569; font-size: 0.85rem; border-top: 1px solid #334155; padding-top: 25px; font-weight: 500;'>News Scraper | High-Visibility Intelligence Dashboard | 2026</div>", unsafe_allow_html=True)
