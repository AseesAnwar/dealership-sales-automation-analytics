import os
import pandas as pd
import streamlit as st
import plotly.express as px
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(
    page_title="Dealership Sales Operations Dashboard",
    page_icon="🚗",
    layout="wide",
)

SHEET_NAME = "Leads"

COLUMN_MAP = {
    "Lead ID": "lead_id",
    "Created At": "created_at",
    "Customer Name": "customer_name",
    "Email": "email",
    "Phone": "phone",
    "Lead Source": "lead_source",
    "Vehicle of Interest": "vehicle",
    "Budget": "budget",
    "Purchase Timeline": "purchase_timeline",
    "Trade-In": "trade_in",
    "Finance Required": "finance_required",
    "Lead Score": "lead_score",
    "Priority": "priority",
    "Assigned To": "assigned_to",
    "Next Action": "next_action",
    "Status": "status",
    "Escalated At": "escalated_at",
    "Escalation Reason": "escalation_reason",
}

@st.cache_data(ttl=60)
def load_demo_data():
    data = [
        ["1","2026-10-06 14:20:00","Taylor Brooks","taylor@example.com","0400111222","Facebook","Kia Sportage SX Hybrid",58000,"Within 7 days","Yes","No",75,"HOT","Digital Sales Team","Call within 10 minutes and book test drive","Escalation Required","2026-10-06 15:00:00","HOT lead remained New for more than 30 minutes"],
        ["2","2026-10-06 15:47:04","QA Test Lead","qa@example.com","0400999888","Google Ads","Kia EV3 GT-Line",54000,"Within 30 days","No","Yes",70,"WARM","Digital Sales Team","Call today and send vehicle options","New","",""],
        ["3","2026-10-06 15:10:00","Emma Carter","emma@example.com","0400100001","Website","Kia Sportage GT-Line Hybrid",61000,"Within 7 days","Yes","Yes",90,"HOT","Digital Sales Team","Call within 10 minutes and book test drive","New","",""],
        ["4","2026-10-06 15:12:00","Noah Wilson","noah@example.com","0400100002","Carsales","Kia Sorento Sport+ Diesel",68000,"Within 30 days","No","Yes",70,"WARM","Digital Sales Team","Call today and send vehicle options","New","",""],
        ["5","2026-10-06 15:14:00","Olivia Martin","olivia@example.com","0400100003","Referral","Kia EV3 GT-Line",54000,"Within 7 days","No","No",75,"HOT","Digital Sales Team","Call within 10 minutes and book test drive","New","",""],
        ["6","2026-10-06 15:16:00","Liam Harris","liam@example.com","0400100004","Facebook","Kia Carnival Sport+",59000,"1-3 months","Yes","Yes",70,"NURTURE","Digital Sales Team","Add to nurture follow-up and check in within 7 days","New","",""],
        ["7","2026-10-06 15:18:00","Ava Thompson","ava@example.com","0400100005","Google Ads","Kia Seltos GT-Line",43000,"Within 30 days","Yes","No",60,"WARM","Digital Sales Team","Call today and send vehicle options","New","",""],
        ["8","2026-10-06 15:20:00","Ethan Clark","ethan@example.com","0400100006","Walk-in","Kia K4 GT-Line",45000,"Within 7 days","No","Yes",75,"HOT","Showroom Sales Team","Call within 10 minutes and book test drive","New","",""],
        ["9","2026-10-06 15:22:00","Mia Anderson","mia@example.com","0400100007","Website","Kia EV5 Air",65000,"3+ months","No","No",35,"NURTURE","Digital Sales Team","Add to nurture follow-up and check in within 7 days","New","",""],
        ["10","2026-10-06 15:24:00","Lucas Walker","lucas@example.com","0400100008","Carsales","Kia Tasman X-Line",70000,"Within 30 days","Yes","Yes",80,"WARM","Digital Sales Team","Call today and send vehicle options","New","",""],
    ]
    return pd.DataFrame(data, columns=list(COLUMN_MAP.keys())).rename(columns=COLUMN_MAP)

@st.cache_data(ttl=60)
def load_google_sheet():
    creds_info = dict(st.secrets["gcp_service_account"])
    sheet_id = st.secrets["google_sheet"]["spreadsheet_id"]

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/drive.readonly",
    ]
    credentials = Credentials.from_service_account_info(creds_info, scopes=scopes)
    client = gspread.authorize(credentials)
    ws = client.open_by_key(sheet_id).worksheet(SHEET_NAME)
    records = ws.get_all_records()
    df = pd.DataFrame(records)
    return df.rename(columns=COLUMN_MAP)

def normalize(df):
    for col in COLUMN_MAP.values():
        if col not in df.columns:
            df[col] = ""
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    df["escalated_at"] = pd.to_datetime(df["escalated_at"], errors="coerce")
    df["lead_score"] = pd.to_numeric(df["lead_score"], errors="coerce").fillna(0)
    df["budget"] = pd.to_numeric(df["budget"], errors="coerce").fillna(0)
    return df

st.title("Dealership Sales Operations Dashboard")
st.caption("Portfolio project • Make.com + Google Sheets + Streamlit")

source_mode = st.sidebar.radio("Data source", ["Google Sheets", "Demo data"], horizontal=False)

try:
    if source_mode == "Google Sheets":
        df = normalize(load_google_sheet())
        st.sidebar.success("Live Google Sheets connection")
    else:
        df = normalize(load_demo_data())
        st.sidebar.info("Using built-in demo data")
except Exception as e:
    st.sidebar.warning("Google Sheets connection unavailable — demo data loaded.")
    st.sidebar.caption(str(e))
    df = normalize(load_demo_data())

st.sidebar.header("Filters")

sources = sorted([x for x in df["lead_source"].dropna().unique() if str(x).strip()])
priorities = sorted([x for x in df["priority"].dropna().unique() if str(x).strip()])
statuses = sorted([x for x in df["status"].dropna().unique() if str(x).strip()])
teams = sorted([x for x in df["assigned_to"].dropna().unique() if str(x).strip()])

selected_sources = st.sidebar.multiselect("Lead Source", sources, default=sources)
selected_priorities = st.sidebar.multiselect("Priority", priorities, default=priorities)
selected_statuses = st.sidebar.multiselect("Status", statuses, default=statuses)
selected_teams = st.sidebar.multiselect("Assigned Team", teams, default=teams)

filtered = df[
    df["lead_source"].isin(selected_sources)
    & df["priority"].isin(selected_priorities)
    & df["status"].isin(selected_statuses)
    & df["assigned_to"].isin(selected_teams)
].copy()

total = len(filtered)
hot = int((filtered["priority"] == "HOT").sum())
warm = int((filtered["priority"] == "WARM").sum())
nurture = int((filtered["priority"] == "NURTURE").sum())
escalations = int((filtered["status"] == "Escalation Required").sum())
avg_score = round(filtered["lead_score"].mean(), 1) if total else 0
hot_rate = round((hot / total) * 100, 1) if total else 0

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Total Leads", total)
k2.metric("HOT", hot)
k3.metric("WARM", warm)
k4.metric("NURTURE", nurture)
k5.metric("Escalations", escalations)
k6.metric("HOT Rate", f"{hot_rate}%")

st.divider()

c1, c2 = st.columns(2)

with c1:
    st.subheader("Leads by Source")
    source_counts = filtered.groupby("lead_source", as_index=False).size().rename(columns={"size":"leads"})
    fig = px.bar(source_counts, x="lead_source", y="leads", text_auto=True)
    fig.update_layout(xaxis_title="", yaxis_title="Leads", height=360)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Priority Mix")
    priority_counts = filtered.groupby("priority", as_index=False).size().rename(columns={"size":"leads"})
    fig = px.pie(priority_counts, names="priority", values="leads", hole=0.55)
    fig.update_layout(height=360)
    st.plotly_chart(fig, use_container_width=True)

c3, c4 = st.columns(2)

with c3:
    st.subheader("Average Lead Score by Source")
    score_source = filtered.groupby("lead_source", as_index=False)["lead_score"].mean()
    fig = px.bar(score_source, x="lead_source", y="lead_score", text_auto=".1f")
    fig.update_layout(xaxis_title="", yaxis_title="Average Score", height=360)
    st.plotly_chart(fig, use_container_width=True)

with c4:
    st.subheader("Lead Activity Over Time")
    timeline = (
        filtered.dropna(subset=["created_at"])
        .assign(day=lambda d: d["created_at"].dt.date)
        .groupby("day", as_index=False)
        .size()
        .rename(columns={"size":"leads"})
    )
    fig = px.line(timeline, x="day", y="leads", markers=True)
    fig.update_layout(xaxis_title="", yaxis_title="Leads", height=360)
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Operational Alerts")
a1, a2, a3, a4 = st.columns(4)
a1.metric("HOT + New", int(((filtered["priority"]=="HOT") & (filtered["status"]=="New")).sum()))
a2.metric("Escalation Required", escalations)
a3.metric("Finance Required", int((filtered["finance_required"]=="Yes").sum()))
a4.metric("Trade-In Leads", int((filtered["trade_in"]=="Yes").sum()))

st.subheader("Lead Operations Table")
search = st.text_input("Search customer, vehicle, source or status")
table = filtered.copy()
if search:
    s = search.lower()
    mask = (
        table["customer_name"].astype(str).str.lower().str.contains(s)
        | table["vehicle"].astype(str).str.lower().str.contains(s)
        | table["lead_source"].astype(str).str.lower().str.contains(s)
        | table["status"].astype(str).str.lower().str.contains(s)
    )
    table = table[mask]

show_cols = [
    "created_at","customer_name","vehicle","lead_source","budget","lead_score",
    "priority","assigned_to","next_action","status","escalated_at","escalation_reason"
]
st.dataframe(
    table[show_cols].sort_values("created_at", ascending=False),
    use_container_width=True,
    hide_index=True,
)

st.caption(f"Average lead score: {avg_score} • Dashboard refreshes cached data every 60 seconds.")
