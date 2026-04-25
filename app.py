import streamlit as st
import pandas as pd
import plotly.express as px
import base64

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Executive Care Analytics", layout="wide")

# ---------------- BACKGROUND IMAGE ----------------
def get_base64(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

bin_str = get_base64('backImg.avif')

if bin_str:
    st.markdown(f"""
    <style>
    .stApp {{
        background-image: linear-gradient(160deg, rgba(10,20,35,0.9), rgba(0,50,100,0.5)),
        url("data:image/jpg;base64,{bin_str}");
        background-size: cover;
        background-attachment: fixed;
    }}
    </style>
    """, unsafe_allow_html=True)

# ---------------- UI STYLING ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@300;600;800&display=swap');

.main-title {
    font-family: Orbitron;
    text-align: center;
    font-size: 3rem;
    color: #00f2fe;
}

.kpi-card {
    background: rgba(16,24,40,0.8);
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    margin: 5px;
}

.kpi-label {
    color: #4facfe;
    font-size: 0.8rem;
}

.kpi-value {
    color: white;
    font-size: 2rem;
    font-weight: bold;
}

footer, header {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    df = pd.read_csv("HHS_Unaccompanied_Alien_Children_Program.csv")

    # 🔥 FIX 1: Clean column names properly
    df.columns = df.columns.str.strip().str.replace("*", "", regex=False)

    # 🔥 FIX 2: Convert to numeric
    numeric_cols = [
        'Children apprehended and placed in CBP custody',
        'Children in CBP custody',
        'Children transferred out of CBP custody',
        'Children in HHS Care',
        'Children discharged from HHS Care'
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    df.fillna(0, inplace=True)

    # 🔥 FIX 3: Correct KPI formulas
    df['Transfer Efficiency'] = (
        df['Children transferred out of CBP custody'] /
        df['Children in CBP custody'].replace(0, 1)
    )

    df['Discharge Effectiveness'] = (
        df['Children discharged from HHS Care'] /
        df['Children in HHS Care'].replace(0, 1)
    )

    df['Throughput'] = (
        df['Children discharged from HHS Care'] /
        df['Children apprehended and placed in CBP custody'].replace(0, 1)
    )

    df['Backlog'] = (
        df['Children in CBP custody'] +
        df['Children in HHS Care']
    )

    df['Outcome Stability'] = df['Discharge Effectiveness'].rolling(7).std().fillna(0)

    return df


df = load_data()

# ---------------- DATE FILTER ----------------
if 'Date' in df.columns:
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    start, end = st.date_input("Select Date Range", [df['Date'].min(), df['Date'].max()])
    df = df[(df['Date'] >= pd.to_datetime(start)) & (df['Date'] <= pd.to_datetime(end))]

# 🔥 FIX 4: Take latest AFTER filtering
latest = df.iloc[-1]

# ---------------- TITLE ----------------
st.markdown("<div class='main-title'>CARE TRANSITION OS</div>", unsafe_allow_html=True)

# ---------------- KPI ----------------
c1, c2, c3, c4, c5 = st.columns(5)

def draw_kpi(col, title, val):
    col.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-label'>{title}</div>
        <div class='kpi-value'>{val:.2f}</div>
    </div>
    """, unsafe_allow_html=True)

draw_kpi(c1, "Transfer Efficiency", latest['Transfer Efficiency'])
draw_kpi(c2, "Discharge Effectiveness", latest['Discharge Effectiveness'])
draw_kpi(c3, "Throughput", latest['Throughput'])
draw_kpi(c4, "Backlog", latest['Backlog'])
draw_kpi(c5, "Outcome Stability", latest['Outcome Stability'])

# ---------------- PIPELINE FLOW ----------------
st.subheader("Pipeline Flow")
fig1 = px.area(df, x='Date', y=['Children in CBP custody', 'Children in HHS Care'])
st.plotly_chart(fig1, use_container_width=True)

# ---------------- EFFICIENCY ----------------
col1, col2 = st.columns(2)

with col1:
    fig2 = px.line(df, x='Date', y='Transfer Efficiency', title="Transfer Efficiency")
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    fig3 = px.line(df, x='Date', y='Discharge Effectiveness', title="Discharge Effectiveness")
    st.plotly_chart(fig3, use_container_width=True)

# ---------------- BOTTLENECK ----------------
st.subheader("Backlog Analysis")
fig4 = px.line(df, x='Date', y='Backlog')
st.plotly_chart(fig4, use_container_width=True)

# ---------------- OUTCOME ----------------
st.subheader("Outcome Stability")
fig5 = px.line(df, x='Date', y='Outcome Stability')
st.plotly_chart(fig5, use_container_width=True)

# ---------------- ALERT SYSTEM ----------------
st.markdown("<h2 style='color:white;'>🚨 System Intelligence Alerts</h2>", unsafe_allow_html=True)

def styled_alert(message, color, icon):
    st.markdown(f"""
    <div style="
        background: rgba(16,24,40,0.85);
        border-left: 6px solid {color};
        padding: 18px;
        border-radius: 12px;
        margin-top: 12px;
        box-shadow: 0 0 20px {color}40;
    ">
        <h4 style="color:{color}; margin:0;">
            {icon} {message}
        </h4>
    </div>
    """, unsafe_allow_html=True)

if latest['Backlog'] > 10000:
    styled_alert("CRITICAL: Backlog too high", "#ff4b2b", "🚨")
elif latest['Transfer Efficiency'] < 0.5:
    styled_alert("WARNING: Low transfer efficiency", "#facc15", "⚡")
else:
    styled_alert("System operating efficiently", "#22c55e", "✅")