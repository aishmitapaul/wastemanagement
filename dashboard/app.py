import sys
import os
import smtplib
from email.mime.text import MIMEText

# Fix import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import requests
import pandas as pd
from utils.config import CHANNEL_ID, READ_API_KEY
from streamlit_autorefresh import st_autorefresh
from dotenv import load_dotenv
from utils.database import add_user, login_user
import streamlit as st

load_dotenv()

# ------------------- PAGE CONFIG -------------------
st.set_page_config(page_title="Smart Waste App", layout="centered")

# ------------------- SESSION -------------------
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# ------------------- LOGIN UI -------------------
st.markdown("""
<style>
.main {
    max-width: 420px;
    margin: auto;
    padding-top: 80px;
}

.login-card {
    background: #1c1f26;
    padding: 30px;
    border-radius: 20px;
    box-shadow: 0px 5px 15px rgba(0,0,0,0.5);
}

.title {
    text-align: center;
    font-size: 26px;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

if not st.session_state.logged_in:

    st.markdown('<div class="title">♻️ Smart Waste App</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🔐 Login", "📝 Signup"])

    # LOGIN
    with tab1:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)

        username = st.text_input("👤 Username")
        password = st.text_input("🔒 Password", type="password")

        if st.button("Login"):
            result = login_user(username, password)
            if result:
                st.session_state.logged_in = True
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials")

        st.markdown('</div>', unsafe_allow_html=True)

    # SIGNUP
    with tab2:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)

        new_user = st.text_input("Create Username")
        new_pass = st.text_input("Create Password", type="password")

        if st.button("Signup"):
            add_user(new_user, new_pass)
            st.success("Account created! Please login.")

        st.markdown('</div>', unsafe_allow_html=True)

    st.stop()

# ------------------- LOGOUT -------------------
st.sidebar.markdown("## 👤 Account")

if st.sidebar.button("🚪 Logout"):
    st.session_state.clear()
    st.rerun()

# ------------------- AUTO REFRESH -------------------
st_autorefresh(interval=10000, key="datarefresh")

# ------------------- MOBILE UI -------------------
st.markdown("""
<style>
.card {
    background: #1c1f26;
    padding: 15px;
    margin: 10px 0;
    border-radius: 15px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">♻️ Smart Waste Monitor</div>', unsafe_allow_html=True)

# ------------------- FETCH DATA -------------------
url = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json?api_key={READ_API_KEY}&results=20"
response = requests.get(url)
data = response.json()

feeds = data.get('feeds', [])
df = pd.DataFrame(feeds)

if df.empty:
    st.warning("No data available yet...")
    st.stop()

# ------------------- CLEAN DATA -------------------
df['field1'] = pd.to_numeric(df['field1'], errors='coerce')
df['field2'] = pd.to_numeric(df['field2'], errors='coerce')
df['field3'] = pd.to_numeric(df['field3'], errors='coerce')

df = df.rename(columns={
    "field1": "Bin 1",
    "field2": "Bin 2",
    "field3": "Bin 3"
})

latest = df.iloc[-1]

# ------------------- EMAIL -------------------
def send_email_alert(message):
    sender = "ashmitapaul436@gmail.com"
    password = os.getenv("EMAIL_PASSWORD") or st.secrets["EMAIL_PASSWORD"]
    receiver = "aishmitapaul84@gmail.com"

    msg = MIMEText(message)
    msg['Subject'] = "🚨 Waste Alert"
    msg['From'] = sender
    msg['To'] = receiver

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())
        server.quit()
    except:
        pass

# ------------------- CARDS -------------------
def get_color(value):
    if value < 50:
        return "#2ecc71"
    elif value < 80:
        return "#f1c40f"
    else:
        return "#e74c3c"

for bin_name in ["Bin 1", "Bin 2", "Bin 3"]:
    value = latest[bin_name]
    color = get_color(value)

    st.markdown(f"""
    <div class="card">
        <h4>{bin_name}</h4>
        <h2 style="color:{color}">{value}%</h2>
    </div>
    """, unsafe_allow_html=True)

# ------------------- ALERTS -------------------
if 'alerts_sent' not in st.session_state:
    st.session_state.alerts_sent = {}

def check_alert(bin_name, value):
    if value > 80:
        st.warning(f"🚨 {bin_name} FULL")

        if bin_name not in st.session_state.alerts_sent:
            send_email_alert(f"{bin_name} is full!")
            st.session_state.alerts_sent[bin_name] = True

for bin_name in ["Bin 1", "Bin 2", "Bin 3"]:
    check_alert(bin_name, latest[bin_name])

# ------------------- GRAPH -------------------
st.markdown("### 📈 Trends")
st.line_chart(df[["Bin 1", "Bin 2", "Bin 3"]])

# ------------------- PREDICTION -------------------
st.markdown("### 🔮 Prediction")

# Moving averages
df['Bin1_avg'] = df['Bin 1'].rolling(3).mean()
df['Bin2_avg'] = df['Bin 2'].rolling(3).mean()
df['Bin3_avg'] = df['Bin 3'].rolling(3).mean()

# Simple prediction (next trend approximation)
df['Bin1_pred'] = df['Bin1_avg'].shift(1)
df['Bin2_pred'] = df['Bin2_avg'].shift(1)
df['Bin3_pred'] = df['Bin3_avg'].shift(1)

# Graphs (clean UI)
st.line_chart(df[['Bin 1', 'Bin1_avg', 'Bin1_pred']])
st.line_chart(df[['Bin 2', 'Bin2_avg', 'Bin2_pred']])
st.line_chart(df[['Bin 3', 'Bin3_avg', 'Bin3_pred']])

# ------------------- STATUS -------------------
def get_status(value):
    if value < 50:
        return "🟢 Low"
    elif value < 80:
        return "🟡 Medium"
    else:
        return "🔴 High"

st.markdown("### 📊 Status")

for bin_name in ["Bin 1", "Bin 2", "Bin 3"]:
    st.write(f"{bin_name}: {get_status(latest[bin_name])}")
