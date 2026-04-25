import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import base64

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Executive Care Analytics", layout="wide")

# ---------------- IMAGE ENCODING ----------------
def get_base64(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return None

# Using the uploaded image file
bin_str = get_base64('backImg.avif')

if bin_str:
    bg_style = f"""
    <style>
    .stApp {{
        background-image: linear-gradient(160deg, rgba(10, 20, 35, 0.92) 20%, rgba(0, 50, 100, 0.4) 100%), url("data:image/jpg;base64,{bin_str}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    </style>
    """
else:
    bg_style = """<style>.stApp { background: #0a192f; }</style>"""

# ---------------- STYLING & ANIMATIONS ----------------
st.markdown(bg_style, unsafe_allow_html=True)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@300;600;800&display=swap');

.block-container {
    background: rgba(255, 255, 255, 0.03);
    border-radius: 30px;
    padding: 3rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(25px);
    margin-top: 25px;
}

.main-title {
    font-family: 'Orbitron', sans-serif;
    text-align: center;
    font-size: 3.8rem;
    font-weight: 800;
    margin-bottom: 0px;
    background: linear-gradient(90deg, #00f2fe, #4facfe, #00f2fe);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: flow 3s linear infinite;
    text-shadow: 0 0 20px rgba(79, 172, 254, 0.3);
}

@keyframes flow { to { background-position: 200% center; } }

.kpi-card {
    background: rgba(16, 24, 40, 0.7);
    padding: 25px;
    border-radius: 20px;
    text-align: center;
    border-bottom: 3px solid #4facfe;
    transition: all 0.4s ease;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}

.kpi-card:hover {
    transform: translateY(-10px) scale(1.02);
    border-bottom: 3px solid #00f2fe;
    background: rgba(16, 24, 40, 0.9);
    box-shadow: 0 0 25px rgba(0, 242, 254, 0.2);
}

.kpi-label {
    color: #4facfe;
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 2px;
}

.kpi-value {
    color: #ffffff;
    font-size: 2.8rem;
    font-weight: 800;
    font-family: 'Orbitron', sans-serif;
    margin-top: 10px;
}

footer, header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ---------------- DATA SOURCE ----------------
@st.cache_data
def load_data():
    df = pd.read_csv("HHS_Unaccompanied_Alien_Children_Program.csv")
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date']).sort_values('Date')
    cols = ['Children apprehended and placed in CBP custody*', 'Children in CBP custody', 
            'Children transferred out of CBP custody', 'Children in HHS Care', 'Children discharged from HHS Care']
    for col in cols:
        if df[col].dtype == 'object':
            df[col] = df[col].str.replace(',', '').astype(float)
    df.fillna(0, inplace=True)
    df['Transfer Efficiency'] = df['Children transferred out of CBP custody'] / df['Children in CBP custody'].replace(0,1)
    df['Discharge Effectiveness'] = df['Children discharged from HHS Care'] / df['Children in HHS Care'].replace(0,1)
    df['Throughput'] = df['Children discharged from HHS Care'] / df['Children apprehended and placed in CBP custody*'].replace(0,1)
    df['Backlog'] = df['Children apprehended and placed in CBP custody*'] - df['Children discharged from HHS Care']
    return df

df = load_data()
latest = df.iloc[-1]

# ---------------- UI LAYOUT ----------------
st.markdown("<div class='main-title'>CARE TRANSITION OS</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#94a3b8; font-family:Inter;'>Real-time Operational Logistics Monitoring</p>", unsafe_allow_html=True)

st.write("##")

# KPI Row
c1, c2, c3, c4 = st.columns(4)
def draw_kpi(col, title, val):
    col.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-label'>{title}</div>
        <div class='kpi-value'>{val:.2f}</div>
    </div>
    """, unsafe_allow_html=True)

draw_kpi(c1, "Pipeline Efficiency", latest['Transfer Efficiency'])
draw_kpi(c2, "Discharge Velocity", latest['Discharge Effectiveness'])
draw_kpi(c3, "System Throughput", latest['Throughput'])
draw_kpi(c4, "Unprocessed Load", latest['Backlog'])

st.write("###")

# ---------------- GRAPHS SECTION ----------------
chart_col_left, chart_col_right = st.columns([2, 1])

theme_config = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color="#e2e8f0", family="Inter"),
    xaxis=dict(showgrid=False, zeroline=False),
    yaxis=dict(gridcolor='rgba(255,255,255,0.05)', zeroline=False)
)

with chart_col_left:
    st.markdown("<p style='color:#00f2fe; font-weight:bold; letter-spacing:1px;'>TRANSITION FLOW ANALYSIS</p>", unsafe_allow_html=True)
    fig_main = px.area(
        df, x='Date', 
        y=['Children apprehended and placed in CBP custody*', 'Children discharged from HHS Care'],
        color_discrete_sequence=["#4facfe", "#00f2fe"]
    )
    fig_main.update_layout(theme_config, margin=dict(t=10))
    st.plotly_chart(fig_main, use_container_width=True)

with chart_col_right:
    st.markdown("<p style='color:#ff4b2b; font-weight:bold; letter-spacing:1px;'>BOTTLE-NECK INDEX</p>", unsafe_allow_html=True)
    fig_side = px.line(df, x='Date', y='Backlog', color_discrete_sequence=["#ff4b2b"])
    fig_side.update_layout(theme_config, margin=dict(t=10))
    st.plotly_chart(fig_side, use_container_width=True)

# ---------------- FOOTER ALERTS ----------------
st.write("##")
bot1, bot2 = st.columns(2)

with bot1:
    st.markdown("""
    <div style='background:rgba(79, 172, 254, 0.1); padding:20px; border-radius:15px; border:1px solid rgba(79, 172, 254, 0.3);'>
        <h4 style='color:#4facfe; margin-top:0;'>AI Insights</h4>
        <p style='color:#cbd5e1;'>System load monitoring is <b>active</b>. Current efficiency trends reflect standard operating capacity. Monitor discharge rates to maintain equilibrium.</p>
    </div>
    """, unsafe_allow_html=True)

with bot2:
    if latest['Backlog'] > 1000:
        st.error("⚠️ CRITICAL: Backlog exceeds safety thresholds. Immediate resource scaling required.")
    else:
        st.success("✅ OPTIMAL: Pipeline flow is within standard operating parameters.")