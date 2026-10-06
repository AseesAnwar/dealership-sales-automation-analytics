# Single-Screen Executive Dashboard Redesign

## Objective

Redesign the Executive Overview page so it behaves like a **Power BI / Tableau dashboard canvas**.

The full dashboard must be visible on a typical laptop/desktop screen **without vertical scrolling**.

The reference image is the target design language and information density.

This is NOT a standard Streamlit analytics page.

It should feel like a fixed executive dashboard canvas.

---

# Non-Negotiable Requirements

## 1. No Sidebar

Remove the Streamlit sidebar from the Executive Overview page.

Do not place filters vertically on the left.

Filters should be moved into a compact top filter bar.

---

## 2. No Vertical Scrolling on Executive Overview

The Executive Overview must fit within a single desktop viewport.

Target design size:

- 16:9 dashboard canvas
- optimised around 1440x900 / 1536x864 / 1920x1080
- everything visible at once
- no need to scroll to see KPI cards, charts, status table, or alerts

Avoid tall spacing.

Avoid large chart heights.

Avoid default Streamlit padding.

---

## 3. Fixed Dashboard Grid

Use a dense CSS grid.

Suggested layout:

### Row 1 — Header
Height: compact

Left:
Dealership Sales Automation System

Subtitle:
Automated Lead Intake • Scoring • SLA Monitoring • Escalation • Analytics

Right:
small stack/tool badges:
- Make.com
- Google Sheets
- Python
- Analytics

Do not make the header taller than necessary.

---

### Row 2 — KPI Cards

One compact row of KPI cards.

Suggested cards:

- Total Leads
- HOT
- WARM
- NURTURE
- New / Uncontacted
- Escalations
- Avg Lead Score
- HOT Rate
- Finance Required
- Trade-In

Cards should be short and wide.

No large white space.

---

### Row 3 — Main Visuals

Use three columns:

Left:
Leads by Source

Center:
Priority Mix

Right:
Leads by Status

All three charts must fit side-by-side.

Chart height target:
approximately 220–260px.

Do not use full-width charts.

---

### Row 4 — Operational Data

Use two columns.

Left:
Compact lead table

Right:
Operational / SLA panel

The lead table should show only the most important fields:

- Customer
- Source
- Vehicle
- Score
- Priority
- Assigned To
- Status

Limit visible rows to 6–8.

Do not show the full dataset here.

The full table belongs on the Lead Operations page.

---

### Row 5 — Bottom Summary Strip

Compact cards / mini-metrics:

- HOT + New
- SLA Breaches
- Digital Sales Team
- Showroom Sales Team
- Finance Leads
- Trade-In Leads

This should be a thin horizontal strip.

---

# Filters

Place filters in a compact toolbar directly below the header.

Suggested controls:

- Date Range
- Lead Source
- Priority
- Status
- Team

Use compact dropdowns.

Do not use large Streamlit multiselect chips that consume multiple lines.

If necessary, use selectbox / segmented control / popover patterns.

Filters must not take more than one row.

---

# Layout Behaviour

Use custom CSS to reduce Streamlit default spacing.

Target:

- minimal top padding
- minimal block gaps
- compact chart margins
- compact text
- small but readable typography
- no unnecessary section headers

Set max-width appropriately so the dashboard feels like a designed canvas rather than a stretched webpage.

Use a centered dashboard container.

---

# Executive Overview Page Only

The one-screen constraint applies specifically to **Executive Overview**.

Other pages can scroll if needed:

- Lead Operations
- Source Analytics
- SLA & Performance

Do not force every page into one screen.

---

# Visual Style

Match the reference image more closely.

Use:

- dark navy header
- white background
- compact rounded cards
- subtle blue-grey borders
- restrained colours
- dashboard-style typography
- clear section boundaries
- table with light row dividers
- small status pills

Avoid:

- oversized Streamlit widgets
- huge empty margins
- tall chart containers
- stacked sections
- left sidebar
- generic app-layout feel

---

# Chart Styling

Use Plotly with:

- small margins
- no unnecessary toolbar clutter
- transparent backgrounds
- small legends
- compact axis labels
- labels inside bars where possible
- consistent category colours

Priority colours:

HOT = red
WARM = amber
NURTURE = green

Keep charts visually dense.

---

# Streamlit Configuration

Use wide layout.

Override default spacing with CSS.

Avoid relying exclusively on st.columns if it produces vertical gaps.

Where necessary, use custom HTML/CSS containers and CSS grid to control placement.

The Executive Overview should render as a dashboard canvas, not as a standard document flow.

---

# Responsiveness

Desktop-first.

For wide screens:
- show full canvas

For narrower screens:
- allow graceful scaling or horizontal reflow

But do not compromise the desktop one-screen layout.

---

# Acceptance Criteria

The Executive Overview is complete only if:

1. There is no sidebar.
2. There is no vertical scrolling at 1440x900 or larger.
3. KPI cards, 3 charts, compact table, and SLA summary are all visible at once.
4. Filters are in a single compact top row.
5. The layout resembles a Power BI/Tableau dashboard rather than a Streamlit demo.
6. The page visually resembles the supplied reference image.
7. Charts and KPIs still update from filters.
8. Google Sheets and demo modes continue to work.
9. Other pages remain functional.
10. No backend logic is broken.

---

# Important

Do NOT solve this by simply shrinking every font.

The goal is proper dashboard composition:
- fixed grid
- compact information hierarchy
- deliberate sizing
- purpose-built executive canvas

---

# Suggested Implementation Strategy

1. Create a dedicated Executive Overview layout component.
2. Use custom CSS grid for the whole page.
3. Place filters in a top toolbar.
4. Render KPI cards in a compact row.
5. Render 3 charts in a 3-column grid.
6. Add a compact lead table and SLA panel side-by-side.
7. Reduce default Streamlit padding/margins.
8. Test at 1440x900, 1536x864, and 1920x1080.
9. Adjust chart heights and card spacing until no vertical scroll remains.

---

# Design Goal

The final Executive Overview should look like a professional single-screen BI dashboard that could plausibly have been built in Power BI or Tableau, while retaining Streamlit interactivity and the existing Google Sheets backend.
