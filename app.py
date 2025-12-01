import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ------------------------
# COLORS & CONSTANTS
# ------------------------
RED = "#E31837"       # Fairfield red
ORANGE = "#FF6B35"    # Residents
GREEN = "#2ECC71"     # Commuters
BLUE = "#3498DB"      # Faculty

FILE = "fairfield_parking.xlsx"

# Category-level capacities
CAPACITY = {
    "Orange (Residents)": 320,   # total resident spaces
    "Green (Commuters)": 480,    # total commuter spaces
    "Blue (Faculty)": 200,       # total faculty spaces
}

# Specific lots inside each category (from the campus map)
LOTS = {
    "Orange (Residents)": [
        "F-1", "F-2", "H-2", "I-1", "M-2"
    ],
    "Green (Commuters)": [
        "B-1", "B-2", "B-3", "E-1", "H-1", "M-1", "N-1", "N-2"
    ],
    "Blue (Faculty)": [
        "A-1", "A-2", "A-3",
        "C-4", "C-5",
        "D-1",
        "G-1", "G-2", "G-3",
        "J-1", "J-2", "J-3",
        "K-1", "K-2", "K-3",
        "O-1",
    ],
}

# Destination → recommended lot per category (simple suggestions)
DEST_RECOMMEND = {
    "Barone Campus Center (BCC)": {
        "Orange (Residents)": "H-2",
        "Green (Commuters)": "B-1",
        "Blue (Faculty)": "C-4",
    },
    "Dolan School of Business": {
        "Orange (Residents)": "M-2",
        "Green (Commuters)": "E-1",
        "Blue (Faculty)": "D-1",
    },
    "RecPlex": {
        "Orange (Residents)": "H-2",
        "Green (Commuters)": "H-1",
        "Blue (Faculty)": "G-1",
    },
    "Library": {
        "Orange (Residents)": "F-1",
        "Green (Commuters)": "B-2",
        "Blue (Faculty)": "K-1",
    },
    "Townhouses": {
        "Orange (Residents)": "F-2",
        "Green (Commuters)": "N-1",
        "Blue (Faculty)": "O-1",
    },
    "The Village / Regis area": {
        "Orange (Residents)": "H-2",
        "Green (Commuters)": "H-1",
        "Blue (Faculty)": "J-1",
    },
    "Dolan Campus": {
        "Orange (Residents)": "M-2",
        "Green (Commuters)": "M-1",
        "Blue (Faculty)": "D-1",
    },
}

# ------------------------
# HELPERS
# ------------------------

def load_data():
    """Load parking history from Excel, or create empty DataFrame."""
    if os.path.exists(FILE) and os.path.getsize(FILE) > 100:
        df = pd.read_excel(FILE)
    else:
        df = pd.DataFrame(columns=["Plate", "Lot", "Entry", "Exit"])
    # make sure columns exist
    for col in ["Plate", "Lot", "Entry", "Exit"]:
        if col not in df.columns:
            df[col] = None
    df["Entry"] = pd.to_datetime(df["Entry"], errors="coerce")
    df["Exit"] = pd.to_datetime(df["Exit"], errors="coerce")
    return df


def save_data(df: pd.DataFrame):
    df.to_excel(FILE, index=False)


def active_in_group(df: pd.DataFrame, group: str) -> pd.DataFrame:
    """Return active cars in a group (Orange, Green, Blue)."""
    return df[(df["Lot"] == group) & df["Exit"].isna()].copy()


def format_free_spaces(free: int, capacity: int) -> str:
    """Return free space text with traffic-light emoji."""
    if free <= 0:
        return "🔴 FULL"
    ratio = free / capacity
    if ratio <= 0.25:
        return f"🟡 {free}"
    return f"🟢 {free}"


# ------------------------
# STREAMLIT SETUP & STYLES
# ------------------------
st.set_page_config(page_title="Fairfield U Parking", layout="wide")

st.markdown("""
<style>
    #MainMenu, footer, header {visibility: hidden;}
    .stApp {background: #fdfdfd;}
    .title-box {
        background:white;
        padding:20px;
        border-radius:15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        text-align:center;
        margin:20px;
    }
    .title {
        color:#E31837;
        font-size:48px;
        font-weight:bold;
        margin:0;
        letter-spacing:2px;
    }
    .subtitle {
        color:#666;
        font-size:20px;
        margin:5px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown(
    """
    <div class="title-box">
        <div class="title">FAIRFIELD UNIVERSITY</div>
        <div class="subtitle">Campus Parking System</div>
    </div>
    """,
    unsafe_allow_html=True,
)

col_header_left, col_header_right = st.columns([5, 1])
with col_header_right:
    st.image(
        "https://www.fairfield.edu/images/fairfield-university-logo.png",
        width=130,
    )

# Load data
df = load_data()

# ------------------------
# SIDEBAR: NAV + PARK IN / OUT
# ------------------------
with st.sidebar:
    st.image(
        "https://www.fairfield.edu/images/fairfield-university-logo.png",
        width=100,
    )
    st.markdown(
        "<h2 style='color:#E31837; margin-bottom:0;'>Navigation</h2>",
        unsafe_allow_html=True,
    )

    page = st.radio(
        "Go to",
        [
            "Orange Lot",
            "Green Lot",
            "Blue Lot",
            "Alerts & Recommendations",
            "Map & Walking",
            "History",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown(
        f"<h2 style='color:{RED}; margin-bottom:0.5rem;'>Park / Exit</h2>",
        unsafe_allow_html=True,
    )

    plate = st.text_input(
        "License Plate",
        placeholder="ABC 123",
    ).upper().strip()

    lot_group = st.selectbox(
        "Lot type",
        list(CAPACITY.keys()),
        help="Orange = residents, Green = commuters, Blue = faculty.",
    )

    c1, c2 = st.columns(2)

    # PARK IN
    if c1.button("PARK IN", use_container_width=True):
        if not plate:
            st.error("Please enter a license plate.")
        elif plate in df[df["Exit"].isna()]["Plate"].values:
            st.error("This plate is already parked on campus.")
        elif len(active_in_group(df, lot_group)) >= CAPACITY[lot_group]:
            st.error("This lot type is full. Choose another one.")
        else:
            new = pd.DataFrame(
                {
                    "Plate": [plate],
                    "Lot": [lot_group],
                    "Entry": [datetime.now()],
                    "Exit": [None],
                }
            )
            df = pd.concat([df, new], ignore_index=True)
            save_data(df)
            st.success(f"{plate} parked in {lot_group}.")
            st.rerun()

    # PARK OUT
    if c2.button("PARK OUT", use_container_width=True):
        active_mask = (df["Plate"] == plate) & df["Exit"].isna()
        if not plate:
            st.error("Please enter a license plate.")
        elif active_mask.any():
            df.loc[active_mask, "Exit"] = datetime.now()
            save_data(df)
            st.success(f"{plate} exited campus parking.")
            st.rerun()
        else:
            st.error("That plate is not currently parked.")

    st.markdown("---")
    st.markdown("**Free space legend**")
    st.write("🟢 plenty • 🟡 getting full • 🔴 full")
    st.markdown("---")
    st.markdown("**Lot meanings**")
    st.write("🟧 **Orange** – Resident student parking.")
    st.write("🟩 **Green** – Commuter & nonresident parking.")
    st.write("🟦 **Blue** – Faculty & staff parking.")

# ------------------------
# MAIN PAGES
# ------------------------

def render_group_page(group_name: str, color: str, title_text: str, description: str):
    """Helper for Orange / Green / Blue pages."""
    st.markdown(
        f'<div style="background:{color}; color:white; padding:15px; '
        f'border-radius:12px; font-size:28px; font-weight:bold; text-align:center;">'
        f'{title_text}</div>',
        unsafe_allow_html=True,
    )

    st.write(description)
    st.markdown("**🟢 plenty • 🟡 getting full • 🔴 full**")
    st.markdown("---")

    # Specific lots table
    st.subheader("Lots in this category")

    rows = []
    used_total = len(active_in_group(df, group_name))
    free_total = CAPACITY[group_name] - used_total
    for lot_code in LOTS[group_name]:
        rows.append(
            {
                "Lot": lot_code,
                "Total spaces (category)": CAPACITY[group_name],
                "Currently parked (category)": used_total,
                "Free spaces (category)": format_free_spaces(free_total, CAPACITY[group_name]),
            }
        )

    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("No specific lots configured for this category.")

    st.markdown("---")

    # Active cars in this category
    st.subheader("Cars currently parked here")

    cur = active_in_group(df, group_name)
    if not cur.empty:
        cur = cur.copy()
        cur["Duration"] = (datetime.now() - cur["Entry"]).astype(str).str.split(".").str[0]
        used = len(cur)

        st.metric(
            "Spaces used (category)",
            f"{used} / {CAPACITY[group_name]}",
            delta=f"{CAPACITY[group_name] - used} available",
        )
        st.dataframe(
            cur[["Plate", "Entry", "Duration"]],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.metric(
            "Spaces used (category)",
            f"0 / {CAPACITY[group_name]}",
            delta=f"{CAPACITY[group_name]} available",
        )
        st.info("No cars currently parked in this lot type.")


# ----- ORANGE PAGE -----
if page == "Orange Lot":
    render_group_page(
        "Orange (Residents)",
        ORANGE,
        "ORANGE LOT • Resident Students",
        "Resident parking near halls like Regis, The Village, and Dolan Campus housing.",
    )

# ----- GREEN PAGE -----
elif page == "Green Lot":
    render_group_page(
        "Green (Commuters)",
        GREEN,
        "GREEN LOT • Commuters & Nonresidents",
        "Commuter and nonresident parking near main campus entrances and academic buildings.",
    )

# ----- BLUE PAGE -----
elif page == "Blue Lot":
    render_group_page(
        "Blue (Faculty)",
        BLUE,
        "BLUE LOT • Faculty & Staff",
        "Faculty and staff parking close to academic and administrative buildings.",
    )

# ----- ALERTS & RECOMMENDATIONS -----
elif page == "Alerts & Recommendations":
    st.markdown("## Alerts & Recommendations")

    # Over-parked cars
    st.markdown("### ⏰ Cars parked longer than X hours")

    if df[df["Exit"].isna()].empty:
        st.info("No cars are currently parked on campus.")
    else:
        max_hours = st.slider(
            "Highlight cars parked more than this many hours:",
            min_value=1,
            max_value=24,
            value=4,
        )
        now = datetime.now()
        active = df[df["Exit"].isna()].copy()
        active["Hours parked"] = (now - active["Entry"]).dt.total_seconds() / 3600
        over = active[active["Hours parked"] > max_hours]

        if over.empty:
            st.success(f"No cars have been parked longer than {max_hours} hours.")
        else:
            over_display = over.copy()
            over_display["Hours parked"] = over_display["Hours parked"].round(1)
            st.warning(f"Cars parked longer than {max_hours} hours:")
            st.dataframe(
                over_display[["Plate", "Lot", "Entry", "Hours parked"]],
                use_container_width=True,
                hide_index=True,
            )

    st.markdown("---")

    # Best lot recommendation
    st.markdown("### 🚗 Find a recommended lot")

    dest = st.selectbox(
        "Where are you heading?",
        list(DEST_RECOMMEND.keys()),
    )

    cat_choice_label = st.radio(
        "Who are you?",
        ["Resident (Orange)", "Commuter (Green)", "Faculty/Staff (Blue)"],
        horizontal=True,
    )

    cat_to_group = {
        "Resident (Orange)": "Orange (Residents)",
        "Commuter (Green)": "Green (Commuters)",
        "Faculty/Staff (Blue)": "Blue (Faculty)",
    }
    group = cat_to_group[cat_choice_label]

    if st.button("Suggest a lot"):
        rec = DEST_RECOMMEND.get(dest, {}).get(group)
        used = len(active_in_group(df, group))
        free = CAPACITY[group] - used
        if rec is None:
            st.info("No specific suggestion available for that combination yet.")
        else:
            st.success(
                f"For **{cat_choice_label}** going to **{dest}**, a good choice is lot **{rec}** "
                f"({group})."
            )
            st.write(
                f"Estimated availability for this category: "
                f"{format_free_spaces(free, CAPACITY[group])} out of {CAPACITY[group]} total spaces."
            )

# ----- MAP & WALKING PAGE -----
elif page == "Map & Walking":
    st.markdown("## Campus Map & Walking Info")

    st.write(
        "This page summarizes approximate walking times between key areas on campus "
        "to help choose a parking area."
    )

    walking_times = [
        {"From - To": "Dolan Campus → BCC", "Minutes": 8},
        {"From - To": "BCC → Dolan School of Business", "Minutes": 7},
        {"From - To": "Townhouses → BCC", "Minutes": 8},
        {"From - To": "Village → BCC", "Minutes": 4},
        {"From - To": "Regis Hall → RecPlex", "Minutes": 4},
        {"From - To": "Dolan Campus → Dolan School of Business", "Minutes": 15},
    ]
    st.subheader("Approximate walking times")
    st.table(walking_times)

    st.markdown("### Parking zones by area (summary)")
    st.write("**Near BCC / central campus**: C-4, C-5, B-1, B-2")
    st.write("**Near Dolan School of Business**: D-1, E-1, M-1, M-2")
    st.write("**Near RecPlex & Village**: G-1, G-2, G-3, H-1, H-2, J-1, J-2, J-3")
    st.write("**Near Library / Kelley Center**: A-1, A-2, A-3, K-1, K-2, K-3")
    st.write("**Near Townhouse complex**: N-1, N-2, O-1")

# ----- HISTORY -----
else:  # History
    st.markdown("## Full Parking History")
    if df.empty:
        st.info("No parking history yet. Start by parking a car in the sidebar.")
    else:
        st.dataframe(
            df.sort_values("Entry", ascending=False),
            use_container_width=True,
        )

st.caption("Fairfield University • Go Stags!")
