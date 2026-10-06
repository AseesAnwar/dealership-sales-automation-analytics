from datetime import time
from html import escape

import gspread
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from google.oauth2.service_account import Credentials


st.set_page_config(
    page_title="Dealership Sales Operations Dashboard",
    page_icon="🚗",
    layout="wide",
)

SHEET_NAME = "Leads"
REFRESH_SECONDS = 60
LOCAL_TZ = "Australia/Melbourne"

PRIORITY_ORDER = ["HOT", "WARM", "NURTURE"]
STATUS_ORDER = [
    "New",
    "Contacted",
    "Appointment",
    "Test Drive",
    "Sold",
    "Lost",
    "Escalation Required",
]
FUNNEL_STAGES = ["New", "Contacted", "Appointment", "Test Drive", "Sold"]

COLORS = {
    "navy": "#0B2A3D",
    "navy_2": "#0F3A53",
    "bg": "#F7F9FC",
    "card": "#FFFFFF",
    "text": "#111827",
    "muted": "#6B7280",
    "border": "#E5E7EB",
    "HOT": "#DC2626",
    "WARM": "#F59E0B",
    "NURTURE": "#16A34A",
    "Escalation Required": "#B91C1C",
    "New": "#2563EB",
    "Contacted": "#0EA5E9",
    "Appointment": "#7C3AED",
    "Test Drive": "#7C3AED",
    "Sold": "#16A34A",
    "Lost": "#6B7280",
}
SOURCE_PALETTE = ["#0B2A3D", "#1F5D7A", "#2E7FAE", "#7C3AED", "#D99A2B", "#3F995A"]

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

PAGE_CSS = """
<style>
    :root {
        --navy: #0B2A3D;
        --navy-2: #0F3A53;
        --bg: #F7F9FC;
        --card: #FFFFFF;
        --text: #111827;
        --muted: #6B7280;
        --border: #D8E0EA;
        --border-soft: #E9EEF5;
        --radius: 8px;
        --gap: 8px;
        --shadow: 0 1px 2px rgba(15, 23, 42, .045);
        --label-size: .64rem;
        --value-size: 1.02rem;
    }
    .stApp {
        background: var(--bg);
        color: var(--text);
    }
    .block-container {
        padding-top: 2.8rem;
        padding-bottom: 1rem;
        max-width: 1440px;
    }
    .main .block-container {
        padding-left: 5rem;
        padding-right: 5rem;
    }
    h1, h2, h3, p {
        letter-spacing: 0;
    }
    [data-testid="stSidebar"] {
        display: none;
    }
    [data-testid="collapsedControl"] {
        display: none;
    }
    div[data-testid="stHorizontalBlock"] {
        gap: var(--gap);
    }
    div[data-testid="stMetric"] {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 8px;
        min-height: 112px;
        padding: 1rem 1rem .85rem;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
    }
    div[data-testid="stMetricLabel"] p {
        color: var(--muted);
        font-size: .78rem;
        font-weight: 700;
        text-transform: uppercase;
    }
    div[data-testid="stMetricValue"] {
        color: #111827;
        font-weight: 760;
    }
    div[data-testid="stPlotlyChart"] {
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: .45rem;
        background: var(--card);
        box-shadow: var(--shadow);
    }
    .app-nav {
        display: grid;
        grid-template-columns: minmax(0, 1fr) auto;
        gap: .75rem;
        align-items: center;
        margin-bottom: .45rem;
    }
    .app-nav-title {
        font-size: .82rem;
        font-weight: 800;
        color: var(--navy);
        text-transform: uppercase;
        letter-spacing: .03em;
    }
    div[data-testid="stRadio"] {
        margin-bottom: 0;
    }
    div[data-testid="stRadio"] > label {
        display: none;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] {
        gap: 6px;
        align-items: center;
    }
    div[data-testid="stRadio"] label {
        min-height: 28px;
        padding: 0 10px;
        border: 1px solid transparent;
        border-radius: 999px;
        background: transparent;
        color: #4B5563;
        font-size: .78rem;
        font-weight: 700;
        transition: background .12s ease, border-color .12s ease, color .12s ease;
    }
    div[data-testid="stRadio"] label[data-baseweb="radio"] > div:first-child {
        display: none;
    }
    div[data-testid="stRadio"] label[data-baseweb="radio"] input {
        display: none;
    }
    div[data-testid="stRadio"] label:has(input:checked) {
        background: #EAF1F7;
        border-color: #C8D5E2;
        color: var(--navy);
        box-shadow: inset 0 0 0 1px rgba(11, 42, 61, .03);
    }
    div[data-testid="stRadio"] label:hover {
        background: #F2F6FA;
        border-color: var(--border);
    }
    div[data-testid="stRadio"] label p {
        font-size: .78rem;
        line-height: 1;
        font-weight: 750;
    }
    div[data-testid="stRadio"] svg {
        width: 12px;
        height: 12px;
    }
    div[data-testid="stSelectbox"] label,
    div[data-testid="stDateInput"] label {
        font-size: var(--label-size);
        font-weight: 820;
        color: var(--muted);
        text-transform: uppercase;
        margin-bottom: 3px;
        letter-spacing: .01em;
    }
    div[data-testid="stSelectbox"] [data-baseweb="select"],
    div[data-testid="stDateInput"] input {
        min-height: 38px;
        background: #F7F9FC;
        border-radius: var(--radius);
    }
    div[data-testid="stDateInput"] input,
    div[data-testid="stSelectbox"] [data-baseweb="select"] > div {
        font-size: .86rem;
        font-weight: 650;
        color: #111827;
    }
    .exec-canvas {
        height: 820px;
        background: #ffffff;
        border: 1px solid #D8E0EA;
        border-radius: 8px;
        box-shadow: 0 14px 34px rgba(15, 23, 42, .08);
        padding: 12px;
        overflow: hidden;
    }
    .exec-header {
        min-height: 60px;
        background: linear-gradient(135deg, var(--navy) 0%, var(--navy-2) 100%);
        border-radius: var(--radius);
        padding: 10px 16px;
        color: #fff;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        box-shadow: 0 2px 8px rgba(11, 42, 61, .12);
    }
    .exec-header h1 {
        color: #fff;
        font-size: 1.13rem;
        line-height: 1.05;
        margin: 0 0 .28rem 0;
        font-weight: 850;
    }
    .exec-header p {
        margin: 0;
        color: rgba(255,255,255,.80);
        font-size: .72rem;
        font-weight: 550;
    }
    .exec-header-right {
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 6px;
    }
    .exec-badges {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        justify-content: flex-end;
        max-width: 360px;
    }
    .exec-badge {
        min-height: 22px;
        display: inline-flex;
        align-items: center;
        border: 1px solid rgba(255,255,255,.25);
        border-radius: 999px;
        background: rgba(255,255,255,.12);
        color: #fff;
        font-size: .62rem;
        font-weight: 780;
        padding: 0 .48rem;
        white-space: nowrap;
    }
    .last-refresh {
        color: rgba(255,255,255,.66);
        font-size: .61rem;
        font-weight: 650;
        white-space: nowrap;
    }
    .filter-card {
        border: 1px solid #D8E0EA;
        border-radius: 8px;
        background: #F8FAFC;
        padding: 0;
        margin: .18rem 0 .32rem;
        border: 0;
        background: transparent;
    }
    .filter-card [data-testid="stHorizontalBlock"] {
        gap: .45rem;
    }
    .filter-card [data-testid="stSelectbox"],
    .filter-card [data-testid="stDateInput"] {
        margin-bottom: 0;
    }
    .exec-kpis {
        display: grid;
        grid-template-columns: repeat(10, minmax(0, 1fr));
        gap: var(--gap);
        margin: 8px 0;
    }
    .exec-kpi {
        height: 54px;
        border: 1px solid var(--border);
        border-radius: var(--radius);
        background: var(--card);
        padding: 7px 8px 6px 10px;
        box-shadow: var(--shadow);
        position: relative;
        overflow: hidden;
    }
    .exec-kpi:before {
        content: "";
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 3px;
        background: var(--accent, #0F3A53);
    }
    .exec-kpi-label {
        color: var(--muted);
        font-size: .59rem;
        line-height: 1.05;
        font-weight: 820;
        text-transform: uppercase;
        letter-spacing: .01em;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .exec-kpi-value {
        color: #111827;
        font-size: var(--value-size);
        line-height: 1.1;
        font-weight: 850;
        margin-top: .24rem;
    }
    .exec-grid-3 {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 8px;
    }
    .exec-grid-2 {
        display: grid;
        grid-template-columns: 1.35fr .9fr;
        gap: 8px;
        margin-top: 8px;
    }
    .exec-panel {
        border: 1px solid #D8E0EA;
        border-radius: 8px;
        background: #FFFFFF;
        padding: 8px;
        min-height: 0;
        overflow: hidden;
    }
    .exec-panel-title {
        color: var(--navy);
        font-size: .68rem;
        font-weight: 860;
        text-transform: uppercase;
        letter-spacing: .012em;
        margin: 0 0 5px;
    }
    .exec-table {
        width: 100%;
        border-collapse: collapse;
        font-size: .7rem;
        border: 1px solid var(--border);
        border-radius: var(--radius);
        overflow: hidden;
        background: var(--card);
        box-shadow: var(--shadow);
    }
    .exec-table th {
        color: var(--muted);
        font-size: .58rem;
        text-align: left;
        text-transform: uppercase;
        padding: 5px 7px;
        border-bottom: 1px solid var(--border-soft);
        white-space: nowrap;
        background: #F8FAFC;
        letter-spacing: .01em;
    }
    .exec-table td {
        height: 28px;
        padding: 4px 7px;
        border-bottom: 1px solid #EEF2F7;
        color: #111827;
        white-space: nowrap;
        max-width: 175px;
        overflow: hidden;
        text-overflow: ellipsis;
        font-weight: 560;
        vertical-align: middle;
    }
    .exec-table tbody tr:nth-child(even) {
        background: #FAFCFE;
    }
    .exec-table tbody tr:last-child td {
        border-bottom: 0;
    }
    .status-pill {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-height: 16px;
        border-radius: 999px;
        color: #fff;
        font-size: .55rem;
        line-height: 1;
        font-weight: 800;
        padding: 0 .42rem;
        white-space: nowrap;
    }
    .sla-panel {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: var(--gap);
    }
    .sla-card {
        border: 1px solid var(--border);
        border-radius: var(--radius);
        background: var(--card);
        padding: 7px 9px;
        height: 52px;
        box-shadow: var(--shadow);
    }
    .sla-card.emphasis {
        border-color: #F1B8B8;
        background: #FFF7F7;
    }
    .sla-label {
        color: var(--muted);
        font-size: .59rem;
        font-weight: 820;
        text-transform: uppercase;
        letter-spacing: .01em;
    }
    .sla-value {
        color: #111827;
        font-size: .98rem;
        font-weight: 850;
        line-height: 1.1;
        margin-top: .22rem;
    }
    .sla-card.emphasis .sla-value {
        color: #B91C1C;
    }
    .bottom-strip {
        display: grid;
        grid-template-columns: repeat(6, 1fr);
        gap: var(--gap);
        margin-top: var(--gap);
    }
    .mini-card {
        border: 1px solid var(--border);
        border-radius: var(--radius);
        background: #F8FAFC;
        padding: 6px 9px;
        height: 48px;
        box-shadow: var(--shadow);
    }
    .mini-label {
        color: var(--muted);
        font-size: .57rem;
        text-transform: uppercase;
        font-weight: 820;
        white-space: nowrap;
        letter-spacing: .01em;
    }
    .mini-value {
        color: #111827;
        font-size: .96rem;
        font-weight: 850;
        line-height: 1.05;
        margin-top: .2rem;
    }
    .hero {
        background: linear-gradient(135deg, #0B2A3D 0%, #0F3A53 100%);
        border-radius: 8px;
        padding: 1.35rem 1.5rem;
        color: white;
        margin-bottom: 1rem;
        box-shadow: 0 8px 22px rgba(11, 42, 61, 0.16);
    }
    .hero h1 {
        color: white;
        font-size: 2rem;
        line-height: 1.15;
        margin: 0 0 .35rem 0;
    }
    .hero p {
        color: rgba(255,255,255,.82);
        margin: 0;
        font-size: .98rem;
    }
    .hero-row {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 1rem;
    }
    .badge {
        display: inline-flex;
        align-items: center;
        border-radius: 999px;
        padding: .22rem .56rem;
        font-size: .72rem;
        font-weight: 750;
        border: 1px solid rgba(255,255,255,.26);
        background: rgba(255,255,255,.12);
        color: white;
        white-space: nowrap;
    }
    .panel {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
    }
    .panel h3 {
        margin: 0 0 .25rem 0;
        font-size: 1rem;
        color: var(--navy);
    }
    .panel p {
        margin: .12rem 0;
        color: var(--muted);
        font-size: .88rem;
    }
    .detail-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: .75rem;
        margin-top: .8rem;
    }
    .detail-item {
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: .75rem;
        background: #FAFBFC;
    }
    .detail-label {
        color: var(--muted);
        font-size: .72rem;
        text-transform: uppercase;
        font-weight: 750;
        margin-bottom: .18rem;
    }
    .detail-value {
        color: var(--text);
        font-weight: 680;
        overflow-wrap: anywhere;
    }
    .action-card {
        border-left: 4px solid #DC2626;
        background: #FFF7F7;
        border-radius: 8px;
        padding: 1rem;
        margin-top: .8rem;
    }
    .pill {
        display: inline-flex;
        border-radius: 999px;
        padding: .16rem .52rem;
        color: white;
        font-size: .7rem;
        font-weight: 760;
        line-height: 1.4;
    }
    .section-kicker {
        color: var(--muted);
        font-size: .8rem;
        font-weight: 750;
        text-transform: uppercase;
        margin-bottom: .15rem;
    }
    .small-note {
        color: var(--muted);
        font-size: .82rem;
    }
    div[data-testid="stDataFrame"] {
        border: 1px solid var(--border);
        border-radius: 8px;
        background: white;
    }
    div[data-testid="stRadio"] label {
        font-size: .92rem;
    }
    @media (max-width: 900px) {
        .exec-canvas {
            height: auto;
            overflow: visible;
        }
        .exec-kpis,
        .exec-grid-3,
        .exec-grid-2,
        .bottom-strip {
            grid-template-columns: 1fr;
        }
        .hero-row,
        .detail-grid {
            grid-template-columns: 1fr;
            display: block;
        }
        .badge {
            margin-top: .8rem;
        }
    }
</style>
"""


@st.cache_data(ttl=REFRESH_SECONDS)
def load_demo_data():
    data = [
        ["1", "2026-10-06 14:20:00", "Taylor Brooks", "taylor@example.com", "0400111222", "Facebook", "Kia Sportage SX Hybrid", 58000, "Within 7 days", "Yes", "No", 75, "HOT", "Digital Sales Team", "Call within 10 minutes and book test drive", "Escalation Required", "2026-10-06 15:00:00", "HOT lead remained New for more than 30 minutes"],
        ["2", "2026-10-06 15:47:04", "QA Test Lead", "qa@example.com", "0400999888", "Google Ads", "Kia EV3 GT-Line", 54000, "Within 30 days", "No", "Yes", 70, "WARM", "Digital Sales Team", "Call today and send vehicle options", "New", "", ""],
        ["3", "2026-10-06 15:10:00", "Emma Carter", "emma@example.com", "0400100001", "Website", "Kia Sportage GT-Line Hybrid", 61000, "Within 7 days", "Yes", "Yes", 90, "HOT", "Digital Sales Team", "Call within 10 minutes and book test drive", "New", "", ""],
        ["4", "2026-10-06 15:12:00", "Noah Wilson", "noah@example.com", "0400100002", "Carsales", "Kia Sorento Sport+ Diesel", 68000, "Within 30 days", "No", "Yes", 70, "WARM", "Digital Sales Team", "Call today and send vehicle options", "Contacted", "", ""],
        ["5", "2026-10-06 15:14:00", "Olivia Martin", "olivia@example.com", "0400100003", "Referral", "Kia EV3 GT-Line", 54000, "Within 7 days", "No", "No", 75, "HOT", "Digital Sales Team", "Confirm availability and send finance options", "Appointment", "", ""],
        ["6", "2026-10-06 15:16:00", "Liam Harris", "liam@example.com", "0400100004", "Facebook", "Kia Carnival Sport+", 59000, "1-3 months", "Yes", "Yes", 70, "NURTURE", "Digital Sales Team", "Add to nurture follow-up and check in within 7 days", "New", "", ""],
        ["7", "2026-10-06 15:18:00", "Ava Thompson", "ava@example.com", "0400100005", "Google Ads", "Kia Seltos GT-Line", 43000, "Within 30 days", "Yes", "No", 60, "WARM", "Digital Sales Team", "Call today and send vehicle options", "Contacted", "", ""],
        ["8", "2026-10-06 15:20:00", "Ethan Clark", "ethan@example.com", "0400100006", "Walk-in", "Kia K4 GT-Line", 45000, "Within 7 days", "No", "Yes", 75, "HOT", "Showroom Sales Team", "Call within 10 minutes and book test drive", "Test Drive", "", ""],
        ["9", "2026-10-06 15:22:00", "Mia Anderson", "mia@example.com", "0400100007", "Website", "Kia EV5 Air", 65000, "3+ months", "No", "No", 35, "NURTURE", "Digital Sales Team", "Add to nurture follow-up and check in within 7 days", "Lost", "", ""],
        ["10", "2026-10-06 15:24:00", "Lucas Walker", "lucas@example.com", "0400100008", "Carsales", "Kia Tasman X-Line", 70000, "Within 30 days", "Yes", "Yes", 80, "WARM", "Digital Sales Team", "Call today and send vehicle options", "Sold", "", ""],
        ["11", "2026-10-06 15:30:00", "Sophie Nguyen", "sophie@example.com", "0400100009", "Website", "Kia EV9 Earth", 98000, "Within 7 days", "Yes", "Yes", 95, "HOT", "Digital Sales Team", "Prioritise manager callback and book EV9 appointment", "Contacted", "", ""],
        ["12", "2026-10-06 15:35:00", "Jack Miller", "jack@example.com", "0400100010", "Carsales", "Kia Picanto GT-Line", 28000, "1-3 months", "No", "No", 40, "NURTURE", "Digital Sales Team", "Send compact car comparison and nurture sequence", "Contacted", "", ""],
        ["13", "2026-10-06 15:38:00", "Grace Young", "grace@example.com", "0400100011", "Google Ads", "Kia Sportage SX Hybrid", 60000, "Within 7 days", "Yes", "Yes", 88, "HOT", "Digital Sales Team", "Call within 10 minutes and lock in test drive", "Escalation Required", "2026-10-06 16:15:00", "HOT lead not contacted inside SLA window"],
        ["14", "2026-10-06 15:41:00", "Henry Scott", "henry@example.com", "0400100012", "Referral", "Kia Sorento GT-Line", 76000, "Within 30 days", "Yes", "Yes", 78, "WARM", "Showroom Sales Team", "Send repayment options and invite to showroom", "Appointment", "", ""],
        ["15", "2026-10-06 15:44:00", "Isla Green", "isla@example.com", "0400100013", "Facebook", "Kia EV5 GT-Line", 72000, "Within 30 days", "No", "Yes", 68, "WARM", "Digital Sales Team", "Follow up with EV stock availability", "Test Drive", "", ""],
        ["16", "2026-10-06 15:50:00", "Leo Brown", "leo@example.com", "0400100014", "Walk-in", "Kia Carnival Platinum", 76000, "Within 7 days", "Yes", "No", 85, "HOT", "Showroom Sales Team", "Manager to call and prepare trade-in valuation", "Sold", "", ""],
    ]
    expected_columns = len(COLUMN_MAP)
    malformed = [row[0] for row in data if len(row) != expected_columns]
    if malformed:
        raise ValueError(f"Demo data rows have the wrong field count: {', '.join(malformed)}")
    return pd.DataFrame(data, columns=list(COLUMN_MAP.keys())).rename(columns=COLUMN_MAP)


@st.cache_data(ttl=REFRESH_SECONDS)
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
    df = df.copy()
    for col in COLUMN_MAP.values():
        if col not in df.columns:
            df[col] = ""
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    df["escalated_at"] = pd.to_datetime(df["escalated_at"], errors="coerce")
    df["lead_score"] = pd.to_numeric(df["lead_score"], errors="coerce").fillna(0)
    df["budget"] = pd.to_numeric(df["budget"], errors="coerce").fillna(0)
    df["priority"] = df["priority"].astype(str).str.strip().str.upper()
    df["status"] = df["status"].replace("", "New").fillna("New")
    df["finance_required"] = df["finance_required"].replace("", "No").fillna("No")
    df["trade_in"] = df["trade_in"].replace("", "No").fillna("No")
    df["lead_id"] = df["lead_id"].astype(str)
    return df


def compact_error(error):
    message = str(error)
    if "No secrets found" in message:
        return "Add .streamlit/secrets.toml to connect the live Google Sheet."
    if "gcp_service_account" in message or "google_sheet" in message:
        return "Check the Google Sheets and service-account entries in secrets.toml."
    return message[:180]


def load_data(source_mode):
    if source_mode == "Google Sheets":
        try:
            return normalize(load_google_sheet()), "Live", None
        except Exception as error:
            return normalize(load_demo_data()), "Demo", compact_error(error)
    return normalize(load_demo_data()), "Demo", None


def option_list(series, preferred_order=None):
    values = [x for x in series.dropna().unique() if str(x).strip()]
    if preferred_order:
        ordered = [value for value in preferred_order if value in values]
        ordered.extend(sorted(value for value in values if value not in ordered))
        return ordered
    return sorted(values)


def date_bounds(df):
    valid = df["created_at"].dropna()
    if valid.empty:
        today = pd.Timestamp.now(tz=LOCAL_TZ).date()
        return today, today
    return valid.min().date(), valid.max().date()


def apply_filters(df, filters):
    filtered = df.copy()
    start_date, end_date = filters["date_range"]
    if start_date and end_date:
        start_dt = pd.Timestamp.combine(start_date, time.min)
        end_dt = pd.Timestamp.combine(end_date, time.max)
        filtered = filtered[
            filtered["created_at"].isna()
            | filtered["created_at"].between(start_dt, end_dt, inclusive="both")
        ]
    for column, selected in [
        ("lead_source", filters["sources"]),
        ("priority", filters["priorities"]),
        ("status", filters["statuses"]),
        ("assigned_to", filters["teams"]),
        ("vehicle", filters["vehicles"]),
    ]:
        if selected:
            filtered = filtered[filtered[column].isin(selected)]
    if filters["finance"] != "Any":
        filtered = filtered[filtered["finance_required"] == filters["finance"]]
    if filters["trade_in"] != "Any":
        filtered = filtered[filtered["trade_in"] == filters["trade_in"]]
    search = filters.get("search", "").strip().lower()
    if search:
        mask = (
            filtered["customer_name"].astype(str).str.lower().str.contains(search, regex=False)
            | filtered["vehicle"].astype(str).str.lower().str.contains(search, regex=False)
            | filtered["lead_source"].astype(str).str.lower().str.contains(search, regex=False)
            | filtered["status"].astype(str).str.lower().str.contains(search, regex=False)
            | filtered["assigned_to"].astype(str).str.lower().str.contains(search, regex=False)
        )
        filtered = filtered[mask]
    return filtered.copy()


def apply_quick_filter(df, quick_filter):
    if quick_filter == "HOT Only":
        return df[df["priority"] == "HOT"].copy()
    if quick_filter == "Escalated":
        return df[df["status"] == "Escalation Required"].copy()
    if quick_filter == "Finance":
        return df[df["finance_required"] == "Yes"].copy()
    if quick_filter == "Trade-In":
        return df[df["trade_in"] == "Yes"].copy()
    if quick_filter == "New / Uncontacted":
        return df[df["status"] == "New"].copy()
    return df.copy()


def local_now():
    return pd.Timestamp.now(tz=LOCAL_TZ)


def as_local(series):
    parsed = pd.to_datetime(series, errors="coerce")
    if getattr(parsed.dt, "tz", None) is None:
        return parsed.dt.tz_localize(LOCAL_TZ, nonexistent="shift_forward", ambiguous="NaT")
    return parsed.dt.tz_convert(LOCAL_TZ)


def with_sla(df):
    enriched = df.copy()
    created_local = as_local(enriched["created_at"])
    now = local_now()
    enriched["minutes_since_created"] = ((now - created_local).dt.total_seconds() / 60).round(0)
    enriched.loc[created_local.isna(), "minutes_since_created"] = pd.NA
    enriched["sla_state"] = "Safe"
    hot_new = (enriched["priority"] == "HOT") & (enriched["status"] == "New")
    enriched.loc[hot_new & (enriched["minutes_since_created"] >= 30), "sla_state"] = "Breached"
    enriched.loc[
        hot_new
        & (enriched["minutes_since_created"] >= 20)
        & (enriched["minutes_since_created"] < 30),
        "sla_state",
    ] = "Close"
    enriched.loc[enriched["status"] == "Escalation Required", "sla_state"] = "Breached"
    return enriched


def kpis(df):
    total = len(df)
    hot = int((df["priority"] == "HOT").sum())
    warm = int((df["priority"] == "WARM").sum())
    nurture = int((df["priority"] == "NURTURE").sum())
    new = int((df["status"] == "New").sum())
    escalations = int((df["status"] == "Escalation Required").sum())
    avg_score = df["lead_score"].mean() if total else 0
    return {
        "total": total,
        "hot": hot,
        "warm": warm,
        "nurture": nurture,
        "new": new,
        "escalations": escalations,
        "avg_score": avg_score,
        "hot_rate": (hot / total * 100) if total else 0,
        "finance": int((df["finance_required"] == "Yes").sum()),
        "trade_in": int((df["trade_in"] == "Yes").sum()),
    }


def sla_metrics(df):
    enriched = with_sla(df)
    hot_df = enriched[enriched["priority"] == "HOT"]
    hot_new = hot_df[hot_df["status"] == "New"]
    breached = hot_df[hot_df["sla_state"] == "Breached"]
    valid_hot = hot_df[hot_df["minutes_since_created"].notna()]
    compliant_count = int((valid_hot["sla_state"] != "Breached").sum())
    compliance = (compliant_count / len(valid_hot) * 100) if len(valid_hot) else None
    today = local_now().date()
    escalated_local = as_local(enriched["escalated_at"])
    escalations_today = int((escalated_local.dt.date == today).sum())
    return {
        "hot": len(hot_df),
        "hot_new": len(hot_new),
        "breached": len(breached),
        "compliance": compliance,
        "escalations_today": escalations_today,
        "queue": enriched[enriched["priority"] == "HOT"].sort_values(
            ["sla_state", "minutes_since_created"],
            ascending=[True, False],
        ),
    }


def status_counts(df, statuses=None):
    statuses = statuses or STATUS_ORDER
    counts = df["status"].value_counts().reindex(statuses, fill_value=0).reset_index()
    counts.columns = ["status", "leads"]
    return counts


def source_kpi_table(df):
    rows = []
    for source, group in df.groupby("lead_source", dropna=False):
        group_kpis = kpis(group)
        rows.append(
            {
                "Source": source,
                "Total Leads": group_kpis["total"],
                "HOT Leads": group_kpis["hot"],
                "WARM Leads": group_kpis["warm"],
                "NURTURE Leads": group_kpis["nurture"],
                "Average Lead Score": round(group_kpis["avg_score"], 1),
                "Finance Required": group_kpis["finance"],
                "Trade-In Leads": group_kpis["trade_in"],
                "Escalations": group_kpis["escalations"],
                "HOT Rate %": round(group_kpis["hot_rate"], 1),
                "Appointments": int((group["status"] == "Appointment").sum()),
                "Test Drives": int((group["status"] == "Test Drive").sum()),
                "Sold": int((group["status"] == "Sold").sum()),
                "Conversion %": round((group["status"].eq("Sold").sum() / len(group) * 100), 1)
                if len(group)
                else 0,
            }
        )
    return pd.DataFrame(rows).sort_values("Total Leads", ascending=False)


def plot_layout(fig, height=340):
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=18, r=18, t=22, b=18),
        font=dict(family="Inter, system-ui, -apple-system, BlinkMacSystemFont, sans-serif"),
        legend_title_text="",
        hoverlabel=dict(bgcolor="white", font_size=12),
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#EEF2F7", zeroline=False)
    return fig


def bar_chart(data, x, y, color=None, title=None, text_auto=True, horizontal=False):
    orientation = "h" if horizontal else "v"
    fig = px.bar(
        data,
        x=x,
        y=y,
        color=color,
        text_auto=text_auto,
        orientation=orientation,
        color_discrete_sequence=SOURCE_PALETTE,
        color_discrete_map=COLORS,
    )
    if title:
        fig.update_layout(title_text=title)
    fig.update_traces(textposition="outside", cliponaxis=False)
    return plot_layout(fig)


def render_header(data_badge, data_error=None):
    badge_label = "Live Google Sheets" if data_badge == "Live" else "Demo data"
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-row">
                <div>
                    <h1>Dealership Sales Operations Dashboard</h1>
                    <p>Make.com + Google Sheets + Streamlit operations cockpit</p>
                </div>
                <span class="badge">{badge_label}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if data_error:
        st.warning(f"Demo data fallback: {data_error}")


def render_kpi_strip(metrics):
    cards = [
        ("Total Leads", f"{metrics['total']:,}", "Filtered lead volume"),
        ("HOT Leads", f"{metrics['hot']:,}", "Immediate sales priority"),
        ("WARM Leads", f"{metrics['warm']:,}", "Active follow-up pool"),
        ("NURTURE Leads", f"{metrics['nurture']:,}", "Longer-cycle buyers"),
        ("New / Uncontacted", f"{metrics['new']:,}", "Awaiting first action"),
        ("Escalations", f"{metrics['escalations']:,}", "SLA or process alerts"),
        ("Average Lead Score", f"{metrics['avg_score']:.1f}", "0-100 scoring model"),
        ("HOT Lead Rate", f"{metrics['hot_rate']:.0f}%", "HOT share of current view"),
        ("Finance Required", f"{metrics['finance']:,}", "Finance opportunity"),
        ("Trade-In Leads", f"{metrics['trade_in']:,}", "Trade-in opportunity"),
    ]
    rows = [cards[:5], cards[5:]]
    for row in rows:
        cols = st.columns(len(row))
        for col, (label, value, help_text) in zip(cols, row):
            col.metric(label, value, help=help_text)


def render_empty(message):
    st.info(message)


def filters_all(df):
    min_date, max_date = date_bounds(df)
    return {
        "date_range": (min_date, max_date),
        "sources": [],
        "priorities": [],
        "statuses": [],
        "teams": [],
        "vehicles": [],
        "finance": "Any",
        "trade_in": "Any",
        "search": "",
    }


def render_top_controls():
    nav_col, data_col = st.columns([0.74, 0.26], vertical_alignment="bottom")
    with nav_col:
        page = st.radio(
            "View",
            ["Executive Overview", "Lead Operations", "Source Analytics", "SLA & Performance"],
            horizontal=True,
        )
    with data_col:
        source_mode = st.radio("Data source", ["Google Sheets", "Demo data"], horizontal=True)
    return page, source_mode


def single_choice_filter(label, values, key):
    options = ["All"] + values
    selected = st.selectbox(label, options, key=key)
    return [] if selected == "All" else [selected]


def executive_filter_bar(df):
    min_date, max_date = date_bounds(df)
    c1, c2, c3, c4, c5 = st.columns([1.45, 1, .85, 1, 1])
    with c1:
        date_range = st.date_input(
            "Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            key="exec_date_range",
        )
        if not isinstance(date_range, tuple) or len(date_range) != 2:
            date_range = (min_date, max_date)
    with c2:
        sources = single_choice_filter("Lead Source", option_list(df["lead_source"]), "exec_source")
    with c3:
        priorities = single_choice_filter("Priority", option_list(df["priority"], PRIORITY_ORDER), "exec_priority")
    with c4:
        statuses = single_choice_filter("Status", option_list(df["status"], STATUS_ORDER), "exec_status")
    with c5:
        teams = single_choice_filter("Team", option_list(df["assigned_to"]), "exec_team")
    return {
        "date_range": date_range,
        "sources": sources,
        "priorities": priorities,
        "statuses": statuses,
        "teams": teams,
        "vehicles": [],
        "finance": "Any",
        "trade_in": "Any",
        "search": "",
    }


def page_filter_expander(df):
    min_date, max_date = date_bounds(df)
    with st.expander("Filters", expanded=False):
        r1c1, r1c2, r1c3, r1c4 = st.columns(4)
        with r1c1:
            date_range = st.date_input(
                "Date range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                key="page_date_range",
            )
            if not isinstance(date_range, tuple) or len(date_range) != 2:
                date_range = (min_date, max_date)
        with r1c2:
            sources = st.multiselect("Lead source", option_list(df["lead_source"]), placeholder="All sources")
        with r1c3:
            priorities = st.multiselect("Priority", option_list(df["priority"], PRIORITY_ORDER), placeholder="All priorities")
        with r1c4:
            statuses = st.multiselect("Status", option_list(df["status"], STATUS_ORDER), placeholder="All statuses")
        r2c1, r2c2, r2c3, r2c4 = st.columns(4)
        with r2c1:
            teams = st.multiselect("Assigned team", option_list(df["assigned_to"]), placeholder="All teams")
        with r2c2:
            vehicles = st.multiselect("Vehicle", option_list(df["vehicle"]), placeholder="All vehicles")
        with r2c3:
            finance = st.selectbox("Finance required", ["Any", "Yes", "No"])
        with r2c4:
            trade_in = st.selectbox("Trade-in", ["Any", "Yes", "No"])
        search = st.text_input("Search")
    return {
        "date_range": date_range,
        "sources": sources,
        "priorities": priorities,
        "statuses": statuses,
        "teams": teams,
        "vehicles": vehicles,
        "finance": finance,
        "trade_in": trade_in,
        "search": search,
    }


def exec_header_html(source_label):
    data_badge = "Live Google Sheets" if source_label == "Live" else "Demo data"
    badges = ["Make.com", "Google Sheets", "Python", "Analytics", data_badge]
    badge_html = "".join(f'<span class="exec-badge">{escape(badge)}</span>' for badge in badges)
    refreshed = local_now().strftime("%d %b %Y, %I:%M %p").lstrip("0")
    return f"""
    <div class="exec-header">
        <div>
            <h1>Dealership Sales Automation System</h1>
            <p>Automated Lead Intake • Scoring • SLA Monitoring • Escalation • Analytics</p>
        </div>
        <div class="exec-header-right">
            <div class="exec-badges">{badge_html}</div>
            <div class="last-refresh">Last refreshed {escape(refreshed)}</div>
        </div>
    </div>
    """


def exec_kpi_cards(metrics):
    cards = [
        ("Total Leads", f"{metrics['total']:,}", COLORS["navy_2"]),
        ("HOT", f"{metrics['hot']:,}", COLORS["HOT"]),
        ("WARM", f"{metrics['warm']:,}", COLORS["WARM"]),
        ("NURTURE", f"{metrics['nurture']:,}", COLORS["NURTURE"]),
        ("New / Uncontacted", f"{metrics['new']:,}", COLORS["New"]),
        ("Escalations", f"{metrics['escalations']:,}", COLORS["Escalation Required"]),
        ("Avg Lead Score", f"{metrics['avg_score']:.1f}", COLORS["navy_2"]),
        ("HOT Rate", f"{metrics['hot_rate']:.0f}%", COLORS["HOT"]),
        ("Finance Required", f"{metrics['finance']:,}", "#0EA5E9"),
        ("Trade-In", f"{metrics['trade_in']:,}", "#7C3AED"),
    ]
    card_html = "".join(
        f'<div class="exec-kpi" style="--accent:{accent};">'
        f'<div class="exec-kpi-label">{escape(label)}</div>'
        f'<div class="exec-kpi-value">{escape(value)}</div>'
        f'</div>'
        for label, value, accent in cards
    )
    return f'<div class="exec-kpis">{card_html}</div>'


def exec_chart_source(df):
    counts = (
        df.groupby("lead_source", as_index=False)
        .size()
        .rename(columns={"size": "leads"})
        .sort_values("leads", ascending=False)
    )
    fig = bar_chart(counts, "lead_source", "leads", color="lead_source") if not counts.empty else go.Figure()
    fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="", height=174, margin=dict(l=4, r=4, t=0, b=10))
    fig.update_xaxes(tickangle=-25, tickfont=dict(size=9))
    fig.update_yaxes(tickfont=dict(size=9), showgrid=False)
    return fig


def exec_chart_priority(df):
    priority_counts = df["priority"].value_counts().reindex(PRIORITY_ORDER, fill_value=0).reset_index()
    priority_counts.columns = ["priority", "leads"]
    priority_counts = priority_counts[priority_counts["leads"] > 0]
    if priority_counts.empty:
        fig = go.Figure()
    else:
        fig = px.pie(
            priority_counts,
            names="priority",
            values="leads",
            hole=0.62,
            color="priority",
            color_discrete_map=COLORS,
        )
        fig.update_traces(textposition="inside", texttemplate="%{label}<br>%{value}")
    fig.update_layout(height=174, margin=dict(l=0, r=0, t=0, b=0), legend=dict(font=dict(size=9), orientation="h", y=-0.08))
    return plot_layout(fig, height=174)


def exec_chart_status(df):
    counts = status_counts(df)
    fig = bar_chart(counts, "leads", "status", color="status", horizontal=True)
    fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="", height=174, margin=dict(l=4, r=6, t=0, b=10))
    fig.update_yaxes(tickfont=dict(size=9))
    fig.update_xaxes(tickfont=dict(size=9), showgrid=False)
    return fig


def exec_lead_table_html(df):
    table = df.sort_values("created_at", ascending=False).head(6)
    rows = []
    for _, lead in table.iterrows():
        priority = escape(str(lead["priority"]))
        status = escape(str(lead["status"]))
        rows.append(
            "<tr>"
            f"<td>{escape(str(lead['customer_name']))}</td>"
            f"<td>{escape(str(lead['lead_source']))}</td>"
            f"<td>{escape(str(lead['vehicle']))}</td>"
            f"<td>{lead['lead_score']:.0f}</td>"
            f"<td><span class=\"status-pill\" style=\"background:{COLORS.get(str(lead['priority']), COLORS['muted'])};\">{priority}</span></td>"
            f"<td>{escape(str(lead['assigned_to']))}</td>"
            f"<td><span class=\"status-pill\" style=\"background:{COLORS.get(str(lead['status']), COLORS['muted'])};\">{status}</span></td>"
            "</tr>"
        )
    if not rows:
        rows.append('<tr><td colspan="7">No leads match the current filters.</td></tr>')
    return (
        '<table class="exec-table"><thead><tr>'
        '<th>Customer</th><th>Source</th><th>Vehicle</th><th>Score</th>'
        '<th>Priority</th><th>Assigned To</th><th>Status</th>'
        f'</tr></thead><tbody>{"".join(rows)}</tbody></table>'
    )


def exec_sla_panel_html(df):
    sla = sla_metrics(df)
    compliance = "N/A" if sla["compliance"] is None else f"{sla['compliance']:.0f}%"
    cards = [
        ("HOT + New", f"{sla['hot_new']:,}"),
        ("SLA Breaches", f"{sla['breached']:,}"),
        ("Escalations Today", f"{sla['escalations_today']:,}"),
        ("SLA Compliance", compliance),
        ("Avg Response Time", "N/A"),
        ("HOT Leads", f"{sla['hot']:,}"),
    ]
    return '<div class="sla-panel">' + "".join(
        f'<div class="sla-card{" emphasis" if label == "SLA Breaches" and value != "0" else ""}"><div class="sla-label">{escape(label)}</div>'
        f'<div class="sla-value">{escape(value)}</div></div>'
        for label, value in cards
    ) + "</div>"


def exec_bottom_strip_html(df):
    sla = sla_metrics(df)
    digital = int((df["assigned_to"] == "Digital Sales Team").sum())
    showroom = int((df["assigned_to"] == "Showroom Sales Team").sum())
    metrics = kpis(df)
    cards = [
        ("HOT + New", f"{sla['hot_new']:,}"),
        ("SLA Breaches", f"{sla['breached']:,}"),
        ("Digital Sales Team", f"{digital:,}"),
        ("Showroom Sales Team", f"{showroom:,}"),
        ("Finance Leads", f"{metrics['finance']:,}"),
        ("Trade-In Leads", f"{metrics['trade_in']:,}"),
    ]
    return '<div class="bottom-strip">' + "".join(
        f'<div class="mini-card"><div class="mini-label">{escape(label)}</div>'
        f'<div class="mini-value">{escape(value)}</div></div>'
        for label, value in cards
    ) + "</div>"


def render_single_screen_overview(df, source_label, source_error):
    st.markdown(exec_header_html(source_label), unsafe_allow_html=True)
    filters = executive_filter_bar(df)
    filtered_df = apply_filters(df, filters)
    metrics = kpis(filtered_df)
    st.markdown(exec_kpi_cards(metrics), unsafe_allow_html=True)

    chart_cols = st.columns(3)
    chart_specs = [
        ("Leads by Source", exec_chart_source(filtered_df)),
        ("Priority Mix", exec_chart_priority(filtered_df)),
        ("Leads by Status", exec_chart_status(filtered_df)),
    ]
    for col, (title, fig) in zip(chart_cols, chart_specs):
        with col:
            st.markdown(f'<div class="exec-panel-title">{title}</div>', unsafe_allow_html=True)
            st.plotly_chart(
                fig,
                width="stretch",
                config={"displayModeBar": False, "responsive": True},
            )

    lower_left, lower_right = st.columns([1.35, .9])
    with lower_left:
        st.markdown(
            f"""
            <div class="exec-panel-title">Priority Lead Queue</div>
            {exec_lead_table_html(filtered_df)}
            """,
            unsafe_allow_html=True,
        )
    with lower_right:
        st.markdown(
            f"""
            <div class="exec-panel-title">Operational / SLA Panel</div>
            {exec_sla_panel_html(filtered_df)}
            """,
            unsafe_allow_html=True,
        )

    st.markdown(exec_bottom_strip_html(filtered_df), unsafe_allow_html=True)
    st.caption(
        f"{source_label} mode • {len(filtered_df):,} leads in current view • "
        f"Cached data refreshes every {REFRESH_SECONDS} seconds."
    )


def render_leads_by_source(df):
    st.subheader("Leads by Source")
    counts = (
        df.groupby("lead_source", as_index=False)
        .size()
        .rename(columns={"size": "leads"})
        .sort_values("leads", ascending=False)
    )
    if counts.empty:
        render_empty("No lead sources match the current filters.")
        return
    fig = bar_chart(counts, "lead_source", "leads", color="lead_source")
    fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Leads")
    st.plotly_chart(fig, width="stretch")


def render_priority_mix(df):
    st.subheader("Priority Mix")
    priority_counts = (
        df["priority"]
        .value_counts()
        .reindex(PRIORITY_ORDER, fill_value=0)
        .reset_index()
    )
    priority_counts.columns = ["priority", "leads"]
    priority_counts = priority_counts[priority_counts["leads"] > 0]
    if priority_counts.empty:
        render_empty("No priority data matches the current filters.")
        return
    fig = px.pie(
        priority_counts,
        names="priority",
        values="leads",
        hole=0.58,
        color="priority",
        color_discrete_map=COLORS,
        custom_data=["leads"],
    )
    fig.update_traces(
        textposition="inside",
        texttemplate="%{label}<br>%{percent}",
        hovertemplate="%{label}: %{customdata[0]} leads<extra></extra>",
    )
    st.plotly_chart(plot_layout(fig), width="stretch")


def render_status_chart(df):
    st.subheader("Leads by Status")
    counts = status_counts(df)
    if counts["leads"].sum() == 0:
        render_empty("No status data matches the current filters.")
        return
    fig = bar_chart(counts, "leads", "status", color="status", horizontal=True)
    fig.update_layout(showlegend=False, xaxis_title="Leads", yaxis_title="")
    st.plotly_chart(fig, width="stretch")


def render_funnel(df):
    st.subheader("Sales Funnel")
    total = len(df)
    previous = None
    funnel_rows = []
    for stage in FUNNEL_STAGES:
        count = int((df["status"] == stage).sum())
        funnel_rows.append(
            {
                "stage": stage,
                "count": count,
                "pct_total": (count / total * 100) if total else 0,
                "dropoff": (previous - count) if previous is not None else 0,
            }
        )
        previous = count
    funnel = pd.DataFrame(funnel_rows)
    if total == 0:
        render_empty("No funnel data matches the current filters.")
        return
    fig = go.Figure(
        go.Funnel(
            y=funnel["stage"],
            x=funnel["count"],
            textinfo="value+percent initial",
            marker=dict(color=[COLORS.get(stage, COLORS["navy_2"]) for stage in funnel["stage"]]),
            connector=dict(line=dict(color="#CBD5E1", width=1)),
        )
    )
    st.plotly_chart(plot_layout(fig, height=320), width="stretch")
    st.dataframe(
        funnel.rename(
            columns={
                "stage": "Stage",
                "count": "Stage Count",
                "pct_total": "% of Total",
                "dropoff": "Drop-Off vs Prior Stage",
            }
        ),
        width="stretch",
        hide_index=True,
        column_config={"% of Total": st.column_config.NumberColumn(format="%.1f%%")},
    )


def render_sla_snapshot(df):
    st.subheader("SLA Snapshot")
    sla = sla_metrics(df)
    compliance = "N/A" if sla["compliance"] is None else f"{sla['compliance']:.0f}%"
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("HOT + New", sla["hot_new"])
    c2.metric("HOT Over 30 Minutes", sla["breached"])
    c3.metric("Escalations Today", sla["escalations_today"])
    c4.metric("SLA Compliance", compliance)
    c5.metric("Average Response Time", "N/A", help="Not available in current dataset")
    st.caption("Average response time is not calculated because no contact timestamp exists in the current schema.")


def style_operations_table(table):
    def row_style(row):
        if row["Status"] == "Escalation Required":
            return ["background-color: #FEF2F2"] * len(row)
        return [""] * len(row)

    return table.style.apply(row_style, axis=1)


def operations_table(df):
    table = df[
        [
            "created_at",
            "customer_name",
            "vehicle",
            "lead_source",
            "budget",
            "purchase_timeline",
            "finance_required",
            "trade_in",
            "lead_score",
            "priority",
            "assigned_to",
            "next_action",
            "status",
            "escalated_at",
        ]
    ].copy()
    table.columns = [
        "Created At",
        "Customer Name",
        "Vehicle",
        "Lead Source",
        "Budget",
        "Purchase Timeline",
        "Finance",
        "Trade-In",
        "Lead Score",
        "Priority",
        "Assigned To",
        "Next Action",
        "Status",
        "Escalated At",
    ]
    return table.sort_values("Created At", ascending=False)


def render_badge(text):
    color = COLORS.get(text, COLORS["muted"])
    return f'<span class="pill" style="background:{color};">{text}</span>'


def render_lead_detail(df):
    st.subheader("Lead Detail")
    if df.empty:
        render_empty("Select filters that return leads to view detail.")
        return
    ordered = df.sort_values("created_at", ascending=False).copy()
    ordered["label"] = (
        ordered["customer_name"].astype(str)
        + " - "
        + ordered["vehicle"].astype(str)
        + " - "
        + ordered["priority"].astype(str)
    )
    selected_label = st.selectbox("Select lead", ordered["label"].tolist())
    lead = ordered[ordered["label"] == selected_label].iloc[0]
    created_local = as_local(pd.Series([lead["created_at"]])).iloc[0]
    minutes_since = None
    if pd.notna(created_local):
        minutes_since = round((local_now() - created_local).total_seconds() / 60)
    remaining = None if minutes_since is None else max(0, 30 - minutes_since)
    sla_state = with_sla(pd.DataFrame([lead])).iloc[0]["sla_state"]

    st.markdown(
        f"""
        <div class="panel">
            <h3>{lead['customer_name']}</h3>
            <p>{lead['vehicle']} from {lead['lead_source']}</p>
            <div style="margin-top:.55rem;">
                {render_badge(lead['priority'])}
                {render_badge(lead['status'])}
            </div>
            <div class="detail-grid">
                <div class="detail-item"><div class="detail-label">Budget</div><div class="detail-value">${lead['budget']:,.0f}</div></div>
                <div class="detail-item"><div class="detail-label">Timeline</div><div class="detail-value">{lead['purchase_timeline']}</div></div>
                <div class="detail-item"><div class="detail-label">Finance</div><div class="detail-value">{lead['finance_required']}</div></div>
                <div class="detail-item"><div class="detail-label">Trade-In</div><div class="detail-value">{lead['trade_in']}</div></div>
                <div class="detail-item"><div class="detail-label">Lead Score</div><div class="detail-value">{lead['lead_score']:.0f}</div></div>
                <div class="detail-item"><div class="detail-label">Assigned Team</div><div class="detail-value">{lead['assigned_to']}</div></div>
                <div class="detail-item"><div class="detail-label">SLA State</div><div class="detail-value">{sla_state}</div></div>
                <div class="detail-item"><div class="detail-label">Elapsed Minutes</div><div class="detail-value">{'N/A' if minutes_since is None else minutes_since}</div></div>
                <div class="detail-item"><div class="detail-label">Remaining SLA Time</div><div class="detail-value">{'N/A' if remaining is None else str(remaining) + ' minutes'}</div></div>
            </div>
            <div class="action-card">
                <div class="detail-label">Recommended Action</div>
                <div class="detail-value">{lead['next_action']}</div>
            </div>
            <p style="margin-top:.8rem;"><strong>Escalation Reason:</strong> {lead['escalation_reason'] or 'None'}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_executive_overview(df):
    render_kpi_strip(kpis(df))
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        render_leads_by_source(df)
    with c2:
        render_priority_mix(df)
    c3, c4 = st.columns(2)
    with c3:
        render_status_chart(df)
    with c4:
        render_funnel(df)
    render_sla_snapshot(df)


def render_quick_filters():
    if "quick_filter" not in st.session_state:
        st.session_state.quick_filter = "All Leads"
    labels = ["All Leads", "HOT Only", "Escalated", "Finance", "Trade-In", "New / Uncontacted"]
    cols = st.columns(len(labels))
    for col, label in zip(cols, labels):
        button_type = "primary" if st.session_state.quick_filter == label else "secondary"
        if col.button(label, type=button_type, width="stretch"):
            st.session_state.quick_filter = label
    return st.session_state.quick_filter


def render_lead_operations(df):
    st.markdown('<div class="section-kicker">Operations Console</div>', unsafe_allow_html=True)
    quick = render_quick_filters()
    active_df = apply_quick_filter(df, quick)
    render_kpi_strip(kpis(active_df))
    st.subheader("Lead Operations Table")
    table = operations_table(active_df)
    st.dataframe(
        style_operations_table(table),
        width="stretch",
        hide_index=True,
        column_config={
            "Created At": st.column_config.DatetimeColumn(format="DD MMM YYYY, h:mm a"),
            "Escalated At": st.column_config.DatetimeColumn(format="DD MMM YYYY, h:mm a"),
            "Budget": st.column_config.NumberColumn(format="$%d"),
            "Lead Score": st.column_config.ProgressColumn(min_value=0, max_value=100),
        },
    )
    render_lead_detail(active_df)


def render_source_charts(df):
    source_table = source_kpi_table(df)
    st.subheader("Source KPI Table")
    if source_table.empty:
        render_empty("No source data matches the current filters.")
    else:
        st.dataframe(
            source_table,
            width="stretch",
            hide_index=True,
            column_config={
                "Average Lead Score": st.column_config.NumberColumn(format="%.1f"),
                "HOT Rate %": st.column_config.NumberColumn(format="%.1f%%"),
                "Conversion %": st.column_config.NumberColumn(format="%.1f%%"),
            },
        )

    c1, c2 = st.columns(2)
    with c1:
        render_leads_by_source(df)
    with c2:
        st.subheader("HOT Rate by Source")
        if source_table.empty:
            render_empty("No HOT-rate data available.")
        else:
            fig = bar_chart(source_table, "Source", "HOT Rate %", color="Source")
            fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="HOT Rate %")
            st.plotly_chart(fig, width="stretch")

    c3, c4 = st.columns(2)
    with c3:
        st.subheader("Average Lead Score by Source")
        if source_table.empty:
            render_empty("No score data available.")
        else:
            fig = bar_chart(source_table, "Source", "Average Lead Score", color="Source")
            fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Average Score")
            st.plotly_chart(fig, width="stretch")
    with c4:
        st.subheader("Escalations by Source")
        if source_table.empty:
            render_empty("No escalation data available.")
        else:
            fig = bar_chart(source_table, "Source", "Escalations", color="Source")
            fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Escalations")
            st.plotly_chart(fig, width="stretch")

    c5, c6 = st.columns(2)
    with c5:
        st.subheader("Finance Leads by Source")
        if source_table.empty:
            render_empty("No finance data available.")
        else:
            fig = bar_chart(source_table, "Source", "Finance Required", color="Source")
            fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Finance Leads")
            st.plotly_chart(fig, width="stretch")
    with c6:
        st.subheader("Trade-In Leads by Source")
        if source_table.empty:
            render_empty("No trade-in data available.")
        else:
            fig = bar_chart(source_table, "Source", "Trade-In Leads", color="Source")
            fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Trade-In Leads")
            st.plotly_chart(fig, width="stretch")


def render_source_drilldown(df):
    st.subheader("Source Drilldown")
    sources = option_list(df["lead_source"])
    if not sources:
        render_empty("No source is available for drilldown.")
        return
    selected_source = st.selectbox("Select source", sources)
    source_df = df[df["lead_source"] == selected_source]
    render_kpi_strip(kpis(source_df))
    c1, c2 = st.columns(2)
    with c1:
        render_priority_mix(source_df)
    with c2:
        render_status_chart(source_df)
    st.subheader("Vehicle Interest Breakdown")
    vehicles = (
        source_df.groupby("vehicle", as_index=False)
        .size()
        .rename(columns={"size": "leads"})
        .sort_values("leads", ascending=False)
    )
    if vehicles.empty:
        render_empty("No vehicle data for this source.")
    else:
        fig = bar_chart(vehicles, "leads", "vehicle", horizontal=True)
        fig.update_layout(xaxis_title="Leads", yaxis_title="")
        st.plotly_chart(fig, width="stretch")
    st.subheader("Leads from Selected Source")
    st.dataframe(operations_table(source_df), width="stretch", hide_index=True)


def render_source_analytics(df):
    render_source_charts(df)
    render_source_drilldown(df)


def render_sla_compliance(df):
    sla = sla_metrics(df)
    compliance = sla["compliance"]
    compliant = 0 if compliance is None else compliance
    breached = 0 if compliance is None else 100 - compliance
    st.subheader("SLA Compliance")
    c1, c2 = st.columns([1, 2])
    with c1:
        st.metric("Compliant", "N/A" if compliance is None else f"{compliant:.0f}%")
        st.metric("Breached", "N/A" if compliance is None else f"{breached:.0f}%")
        st.metric("Total HOT Leads", sla["hot"])
    with c2:
        if compliance is None:
            render_empty("SLA compliance cannot be calculated without valid HOT lead timestamps.")
        else:
            st.progress(int(compliant), text=f"{compliant:.0f}% compliant")
            st.caption("Compliant means HOT leads are not currently breached under the 30-minute New-lead SLA.")


def render_escalation_analysis(df):
    st.subheader("Escalation Analysis")
    escalated = df[df["status"] == "Escalation Required"].copy()
    c1, c2 = st.columns(2)
    with c1:
        by_source = (
            escalated.groupby("lead_source", as_index=False)
            .size()
            .rename(columns={"size": "escalations"})
            .sort_values("escalations", ascending=False)
        )
        st.markdown("**Escalations by Source**")
        if by_source.empty:
            render_empty("No escalations match the current filters.")
        else:
            fig = bar_chart(by_source, "lead_source", "escalations", color="lead_source")
            fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Escalations")
            st.plotly_chart(fig, width="stretch")
    with c2:
        by_team = (
            escalated.groupby("assigned_to", as_index=False)
            .size()
            .rename(columns={"size": "escalations"})
            .sort_values("escalations", ascending=False)
        )
        st.markdown("**Escalations by Team**")
        if by_team.empty:
            render_empty("No team escalations match the current filters.")
        else:
            fig = bar_chart(by_team, "assigned_to", "escalations", color="assigned_to")
            fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Escalations")
            st.plotly_chart(fig, width="stretch")

    c3, c4 = st.columns(2)
    with c3:
        st.markdown("**Escalations Over Time**")
        timeline = (
            escalated.dropna(subset=["escalated_at"])
            .assign(day=lambda d: d["escalated_at"].dt.date)
            .groupby("day", as_index=False)
            .size()
            .rename(columns={"size": "escalations"})
        )
        if timeline.empty:
            render_empty("No dated escalations available.")
        else:
            fig = px.line(timeline, x="day", y="escalations", markers=True)
            fig.update_traces(line=dict(color=COLORS["Escalation Required"], width=3), marker=dict(size=8))
            fig.update_layout(xaxis_title="", yaxis_title="Escalations")
            st.plotly_chart(plot_layout(fig), width="stretch")
    with c4:
        st.markdown("**HOT Leads Awaiting Action**")
        awaiting = df[(df["priority"] == "HOT") & (df["status"] == "New")]
        if awaiting.empty:
            render_empty("No HOT leads are currently awaiting action.")
        else:
            counts = (
                awaiting.groupby("assigned_to", as_index=False)
                .size()
                .rename(columns={"size": "hot_new"})
            )
            fig = bar_chart(counts, "assigned_to", "hot_new", color="assigned_to")
            fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="HOT + New")
            st.plotly_chart(fig, width="stretch")


def render_sla_queue(df):
    st.subheader("SLA Queue")
    queue = with_sla(df)
    queue = queue[queue["priority"] == "HOT"].copy()
    if queue.empty:
        render_empty("No HOT leads match the current filters.")
        return
    risk_order = {"Breached": 0, "Close": 1, "Safe": 2}
    queue["risk_rank"] = queue["sla_state"].map(risk_order).fillna(3)
    queue = queue.sort_values(["risk_rank", "minutes_since_created"], ascending=[True, False])
    display = queue[
        [
            "customer_name",
            "vehicle",
            "created_at",
            "minutes_since_created",
            "status",
            "assigned_to",
            "next_action",
            "sla_state",
        ]
    ].copy()
    display.columns = [
        "Customer",
        "Vehicle",
        "Created At",
        "Minutes Since Created",
        "Status",
        "Assigned Team",
        "Next Action",
        "SLA State",
    ]

    def queue_style(row):
        if row["SLA State"] == "Breached":
            return ["background-color: #FEF2F2"] * len(row)
        if row["SLA State"] == "Close":
            return ["background-color: #FFFBEB"] * len(row)
        return [""] * len(row)

    st.dataframe(
        display.style.apply(queue_style, axis=1),
        width="stretch",
        hide_index=True,
        column_config={
            "Created At": st.column_config.DatetimeColumn(format="DD MMM YYYY, h:mm a"),
            "Minutes Since Created": st.column_config.NumberColumn(format="%d"),
        },
    )


def render_sla_performance(df):
    sla = sla_metrics(df)
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("HOT Leads", sla["hot"])
    c2.metric("HOT + New", sla["hot_new"])
    c3.metric("Escalated HOT Leads", sla["breached"])
    c4.metric("SLA Compliance", "N/A" if sla["compliance"] is None else f"{sla['compliance']:.0f}%")
    c5.metric("Avg Response Time", "N/A", help="Not available in current dataset")
    c6.metric("Escalations Today", sla["escalations_today"])
    render_sla_compliance(df)
    render_escalation_analysis(df)
    render_sla_queue(df)


def sidebar_filters(df, source_label, source_error):
    st.sidebar.markdown("### Navigation")
    page = st.sidebar.radio(
        "Page",
        ["Executive Overview", "Lead Operations", "Source Analytics", "SLA & Performance"],
        label_visibility="collapsed",
    )
    st.sidebar.markdown("### Data")
    st.sidebar.caption(f"Current source: {source_label}")
    if source_error:
        st.sidebar.caption(source_error)
    st.sidebar.markdown("### Global Filters")
    min_date, max_date = date_bounds(df)
    date_range = st.sidebar.date_input("Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    if not isinstance(date_range, tuple) or len(date_range) != 2:
        date_range = (min_date, max_date)
    filters = {
        "date_range": date_range,
        "sources": st.sidebar.multiselect("Lead source", option_list(df["lead_source"]), placeholder="All sources"),
        "priorities": st.sidebar.multiselect("Priority", option_list(df["priority"], PRIORITY_ORDER), placeholder="All priorities"),
        "statuses": st.sidebar.multiselect("Status", option_list(df["status"], STATUS_ORDER), placeholder="All statuses"),
        "teams": st.sidebar.multiselect("Assigned team", option_list(df["assigned_to"]), placeholder="All teams"),
        "vehicles": st.sidebar.multiselect("Vehicle", option_list(df["vehicle"]), placeholder="All vehicles"),
        "finance": st.sidebar.selectbox("Finance required", ["Any", "Yes", "No"]),
        "trade_in": st.sidebar.selectbox("Trade-in", ["Any", "Yes", "No"]),
        "search": st.sidebar.text_input("Search"),
    }
    return page, filters


st.markdown(PAGE_CSS, unsafe_allow_html=True)

page, source_mode = render_top_controls()
df, source_label, source_error = load_data(source_mode)

if page == "Executive Overview":
    render_single_screen_overview(df, source_label, source_error)
else:
    filters = page_filter_expander(df)
    filtered = apply_filters(df, filters)
    render_header(source_label, source_error)
    st.caption("Automated Lead Intake • Scoring • SLA Monitoring • Escalation • Analytics")

    if page == "Lead Operations":
        render_lead_operations(filtered)
    elif page == "Source Analytics":
        render_source_analytics(filtered)
    elif page == "SLA & Performance":
        render_sla_performance(filtered)

    st.caption(
        f"{source_label} mode • {len(filtered):,} leads in current view • "
        f"Cached data refreshes every {REFRESH_SECONDS} seconds."
    )
