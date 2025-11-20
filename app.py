import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Colors
RED = "#E31837"
ORANGE = "#FF6B35"
GREEN = "#2ECC71"
BLUE = "#3498DB"

st.set_page_config(page_title="Fairfield U Parking", layout="wide")

# Clean UI + hide Streamlit junk
st.markdown("""
<style>
    #MainMenu, footer, header {visibility: hidden;}
    .stApp {background: #fdfdfd;}
    .title-box {background:white; padding:20px; border-radius:15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); text-align:center; margin:20px;}
    .title {color:#E31837; font-size:48px; font-weight:bold; margin:0;}
    .subtitle {color:#666; font-size:22px; margin:5px;}
    .nav-button {font-size:18px; font-weight:bold; text-align:left; padding:15px; border-radius:10px; margin:5px 0;}
</style>
""", unsafe_allow_html=True)

# Header with white box
st.markdown(f'''
<div class="title-box">
    <div class="title">FAIRFIELD UNIVERSITY</div>
    <div class="subtitle">Campus Parking System</div>
</div>
''', unsafe_allow_html=True)

col1, col2 = st.columns([5,1])
with col2:
    st.image("https://www.fairfield.edu/images/fairfield-university-logo.png", width=130)

# Load data
FILE = "fairfield_parking.xlsx"
if os.path.exists(FILE) and os.path.getsize(FILE) > 100:
    df = pd.read_excel(FILE)
else:
    df = pd.DataFrame(columns=["Plate", "Lot", "Entry", "Exit"])
df["Entry"] = pd.to_datetime(df["Entry"], errors="coerce")
df["Exit"] = pd.to_datetime(df["Exit"], errors="coerce")

CAPACITY = {"Orange (Residents)": 320, "Green (Commuters)": 480, "Blue (Faculty)": 200}

# === LEFT NAVIGATION ===
with st.sidebar:
    st.image("https://www.fairfield.edu/images/fairfield-university-logo.png", width=100)
    st.markdown("<h2 style='color:#E31837'>Navigation</h2>", unsafe_allow_html=True)
    
    page = st.radio("Go to", 
        ["Orange Lot", "Green Lot", "Blue Lot", "History"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown(f"<h2 style='color:{RED}'>Park / Exit</h2>", unsafe_allow_html=True)
    plate = st.text_input("License Plate", placeholder="ABC 123").upper().strip()
    lot = st.selectbox("Select Lot", list(CAPACITY.keys()))
    
    c1, c2 = st.columns(2)
    if c1.button("PARK IN", use_container_width=True):
        if not plate: st.error("Enter plate!")
        elif plate in df[df["Exit"].isna()]["Plate"].values: st.error("Already parked!")
        elif len(df[(df["Lot"]==lot) & df["Exit"].isna()]) >= CAPACITY[lot]: st.error("LOT FULL!")
        else:
            new = pd.DataFrame({"Plate":[plate],"Lot":[lot],"Entry":[datetime.now()],"Exit":[None]})
            df = pd.concat([df, new], ignore_index=True)
            df.to_excel(FILE, index=False)
            st.success(f"{plate} parked!")
            st.rerun()

    if c2.button("PARK OUT", use_container_width=True):
        if plate in df[df["Exit"].isna()]["Plate"].values:
            df.loc[(df["Plate"]==plate) & df["Exit"].isna(), "Exit"] = datetime.now()
            df.to_excel(FILE, index=False)
            st.success(f"{plate} exited")
            st.rerun()
        else:
            st.error("Not parked")

# === MAIN CONTENT ===
if page == "Orange Lot":
    st.markdown('<div style="background:#FF6B35; color:white; padding:15px; border-radius:12px; font-size:28px; font-weight:bold; text-align:center;">ORANGE LOT • Residents</div>', unsafe_allow_html=True)
    cur = df[(df["Lot"]=="Orange (Residents)") & df["Exit"].isna()].copy()
    cur["Duration"] = (datetime.now() - cur["Entry"]).apply(lambda x: str(x)[:-10])
    st.metric("Spaces Used", f"{len(cur)} / 320", delta=f"{320-len(cur)} available")
    if len(cur)>0:
        st.dataframe(cur[["Plate","Entry","Duration"]], use_container_width=True, hide_index=True)
    else:
        st.info("No residents currently parked")

elif page == "Green Lot":
    st.markdown('<div style="background:#2ECC71; color:white; padding:15px; border-radius:12px; font-size:28px; font-weight:bold; text-align:center;">GREEN LOT • Commuters</div>', unsafe_allow_html=True)
    cur = df[(df["Lot"]=="Green (Commuters)") & df["Exit"].isna()].copy()
    cur["Duration"] = (datetime.now() - cur["Entry"]).apply(lambda x: str(x)[:-10])
    st.metric("Spaces Used", f"{len(cur)} / 480", delta=f"{480-len(cur)} available")
    if len(cur)>0:
        st.dataframe(cur[["Plate","Entry","Duration"]], use_container_width=True, hide_index=True)
    else:
        st.info("No commuters currently parked")

elif page == "Blue Lot":
    st.markdown('<div style="background:#3498DB; color:white; padding:15px; border-radius:12px; font-size:28px; font-weight:bold; text-align:center;">BLUE LOT • Faculty & Staff</div>', unsafe_allow_html=True)
    cur = df[(df["Lot"]=="Blue (Faculty)") & df["Exit"].isna()].copy()
    cur["Duration"] = (datetime.now() - cur["Entry"]).apply(lambda x: str(x)[:-10])
    st.metric("Spaces Used", f"{len(cur)} / 200", delta=f"{200-len(cur)} available")
    if len(cur)>0:
        st.dataframe(cur[["Plate","Entry","Duration"]], use_container_width=True, hide_index=True)
    else:
        st.info("No faculty currently parked")

else:  # History
    st.markdown("### Full Parking History")
    st.dataframe(df.sort_values("Entry", ascending=False), use_container_width=True)

st.caption("Fairfield University • Go Stags!")
