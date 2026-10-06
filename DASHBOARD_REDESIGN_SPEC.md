# Dashboard Redesign Specification

## Goal

Redesign the existing Streamlit dashboard into a polished, premium **Dealership Sales Operations Cockpit** inspired by a modern executive BI dashboard.

The redesigned UI should feel significantly more professional than default Streamlit while preserving the current data pipeline and business logic.

Do **not** rebuild the backend.

Preserve:
- Google Sheets connection
- Demo data fallback
- Existing lead fields
- Existing KPI calculations
- Existing Make.com automation architecture
- Existing Streamlit deployment approach

Focus on:
- visual design
- information hierarchy
- interaction
- filtering
- multi-page navigation
- operational usability
- portfolio presentation quality

---

# Product Positioning

Project name:

**Dealership Sales Automation & Analytics Platform**

Dashboard title:

**Dealership Sales Operations Dashboard**

Subtitle:

**Automated Lead Intake • Scoring • SLA Monitoring • Escalation • Analytics**

The dashboard should look like a credible internal dealership sales-operations product rather than a student dashboard.

---

# Design Direction

Use a premium automotive / executive BI visual language.

## Core visual style

- Dark navy header
- White / soft neutral dashboard background
- Rounded cards
- Subtle borders
- Minimal shadows
- Strong typography hierarchy
- Compact spacing
- Clean chart backgrounds
- Status-based accent colours only where meaningful
- Avoid excessive gradients or decorative effects
- Avoid default Streamlit styling wherever possible

## Suggested palette

Primary navy:
- #0B2A3D
- #0F3A53

Neutral background:
- #F7F9FC
- #FFFFFF

Text:
- #111827
- #374151
- #6B7280

Status colours:
- HOT: #DC2626
- WARM: #F59E0B
- NURTURE: #16A34A
- Escalation: #B91C1C
- New: #2563EB
- Contacted: #0EA5E9
- Appointment/Test Drive: #7C3AED
- Sold: #16A34A
- Lost: #6B7280

Use colour consistently.

---

# Navigation

Create a multi-page Streamlit app using sidebar or top navigation.

Pages:

1. Executive Overview
2. Lead Operations
3. Source Analytics
4. SLA & Performance

If a fifth page improves the architecture, add:

5. Funnel & Conversion

Keep navigation compact and professional.

---

# PAGE 1 — Executive Overview

## Header

Display:

**Dealership Sales Operations Dashboard**

Subtitle:
**Make.com + Google Sheets + Streamlit operations cockpit**

Optional:
small "Live" / "Demo" data source badge.

Do not show technical error messages prominently on the main canvas.

---

## KPI strip

Create a horizontal KPI grid.

Include:

- Total Leads
- HOT Leads
- WARM Leads
- NURTURE Leads
- New / Uncontacted
- Escalations
- Average Lead Score
- HOT Lead Rate
- Finance Required
- Trade-In Leads

Each KPI should have:
- compact label
- prominent number
- optional small contextual subtext
- appropriate status accent
- consistent card height

Do not make every card a different strong colour.
Use mostly neutral cards with restrained accent indicators.

---

## Primary charts

### Leads by Source
Interactive bar chart.

Show:
- Carsales
- Facebook
- Google Ads
- Website
- Referral
- Walk-in

Requirements:
- sort by lead volume descending
- clear data labels
- clean axis formatting
- no chart clutter

### Priority Mix
Donut chart.

Categories:
- HOT
- WARM
- NURTURE

Show percentages and counts.

### Leads by Status
Bar or horizontal bar chart.

Suggested statuses:
- New
- Contacted
- Appointment
- Test Drive
- Sold
- Lost
- Escalation Required

If some statuses do not exist yet in demo data, support them gracefully with zero values.

---

## Sales Funnel

Create an executive funnel:

New
→ Contacted
→ Appointment
→ Test Drive
→ Sold

Show:
- stage count
- percentage of total
- drop-off between stages

If current data only has limited statuses, keep the logic ready and display available stages without errors.

---

## SLA snapshot

Add compact SLA cards:

- HOT + New
- HOT Over 30 Minutes
- Escalations Today
- SLA Compliance %
- Average Response Time (if available)

If response-time data is not yet available, display:
"Not available in current dataset"

Do not fabricate metrics.

---

# PAGE 2 — Lead Operations

This page should feel like an operations console.

## Compact filter bar

Filters:

- Date range
- Lead source
- Priority
- Status
- Assigned team
- Vehicle
- Finance required
- Trade-in
- Search

Use compact controls.
Avoid oversized default multiselects where possible.

---

## Quick-filter buttons

Add:

- All Leads
- HOT Only
- Escalated
- Finance
- Trade-In
- New / Uncontacted

Buttons should update the main table and related KPI counts.

---

## Lead operations table

Show:

- Created At
- Customer Name
- Vehicle
- Lead Source
- Budget
- Purchase Timeline
- Finance
- Trade-In
- Lead Score
- Priority
- Assigned To
- Next Action
- Status
- Escalated At

Requirements:
- sortable where possible
- clean formatting
- currency formatting for Budget
- badges/pills for Priority and Status
- compact row height
- highlight escalated rows subtly
- avoid rainbow styling

---

## Lead detail panel

When a lead is selected, show a detail section with:

Customer
Vehicle
Source
Budget
Timeline
Finance
Trade-In
Lead Score
Priority
Assigned Team
Next Action
Status
Escalation Reason

Add a prominent recommended-action card.

Example:

**Recommended Action**
Call within 10 minutes and book test drive

If SLA timing can be calculated, show:
- elapsed minutes
- remaining SLA time
- breached / compliant state

If timing data is unavailable, omit rather than fabricate.

---

# PAGE 3 — Source Analytics

Goal:
compare acquisition channels.

## Source KPI table

For each source show:

- Total Leads
- HOT Leads
- WARM Leads
- NURTURE Leads
- Average Lead Score
- Finance Required
- Trade-In Leads
- Escalations
- HOT Rate %

If conversion statuses are available, also show:

- Appointments
- Test Drives
- Sold
- Conversion %

---

## Source comparison charts

Include:

- Leads by Source
- HOT Rate by Source
- Average Lead Score by Source
- Escalations by Source
- Finance Leads by Source
- Trade-In Leads by Source

Use bar charts with a consistent visual language.

---

## Source drilldown

Allow selecting one source and seeing:

- KPI summary
- priority mix
- status mix
- lead table
- vehicle interest breakdown

---

# PAGE 4 — SLA & Performance

This page should showcase the automation logic.

## SLA KPI cards

- HOT Leads
- HOT + New
- Escalated HOT Leads
- SLA Compliance %
- Average Response Time
- Escalations Today

Only calculate response-time metrics if valid fields exist.

---

## SLA compliance visual

Use one of:
- progress bar
- bullet chart
- gauge-like card

Avoid flashy speedometer-style gauges.

Show:
- compliant %
- breached %
- total HOT leads

---

## Escalation analysis

Charts:

- Escalations by Source
- Escalations by Team
- Escalations Over Time
- HOT Leads Awaiting Action

---

## SLA queue

Create a table for current HOT leads:

- Customer
- Vehicle
- Created At
- Minutes Since Created
- Status
- Assigned Team
- Next Action

Sort highest-risk leads first.

If possible:

- red = breached
- amber = close to SLA
- neutral = safe

Use Melbourne timezone where timestamps are interpreted.

---

# Global Filters

Where practical, support:

- Date Range
- Lead Source
- Priority
- Status
- Assigned Team
- Vehicle

Filters should affect:
- KPIs
- charts
- tables

Keep filters persistent per page if possible.

---

# Data Requirements

Use the existing Google Sheets schema:

Lead ID
Created At
Customer Name
Email
Phone
Lead Source
Vehicle of Interest
Budget
Purchase Timeline
Trade-In
Finance Required
Lead Score
Priority
Assigned To
Next Action
Status
Escalated At
Escalation Reason

Do not rename source columns in Google Sheets.

Use an internal dataframe mapping if needed.

---

# Data Safety

Important:

- never expose Google credentials
- never commit secrets.toml
- keep service-account credentials in Streamlit secrets
- preserve .gitignore protection
- never log sensitive credential values

The GitHub repository must remain safe for public viewing.

---

# Demo Data

Keep demo mode.

The app must still work if live Google Sheets credentials are unavailable.

Improve the demo dataset to include realistic examples of:

- HOT / WARM / NURTURE
- New
- Contacted
- Appointment
- Test Drive
- Sold
- Lost
- Escalation Required

All demo data must remain clearly synthetic.

---

# Interaction Requirements

The dashboard should feel genuinely interactive.

Required:

- filters update KPIs and charts
- search updates lead table
- source drilldown works
- lead detail selection works
- quick-filter buttons work
- pages share the same data-loading layer
- charts render correctly with empty datasets
- no NaN / None / broken chart errors

---

# Responsive Design

Target primarily desktop and laptop.

Also ensure:
- sidebar does not dominate the screen
- KPI grid wraps gracefully
- tables remain usable
- charts resize with container width
- no major horizontal page overflow

---

# Streamlit Styling Requirements

Use custom CSS where helpful.

Recommended:
- custom page header
- styled KPI cards
- status badges
- compact containers
- reduced default Streamlit whitespace
- polished sidebar
- consistent section headings

Do not:
- hide critical accessibility features
- use brittle DOM selectors excessively
- depend on undocumented class names when avoidable
- inject unsafe external scripts

---

# Plotly Styling

Charts should use:

- transparent or white plot background
- minimal gridlines
- consistent fonts
- responsive layout
- clear hover states
- compact legends
- consistent category colours

Avoid:
- default rainbow colour cycles
- heavy borders
- unnecessary 3D effects
- cluttered axes

---

# File Structure

Refactor if useful:

```text
app.py
dashboard/
    data.py
    metrics.py
    styles.py
    components.py
pages/
    1_Executive_Overview.py
    2_Lead_Operations.py
    3_Source_Analytics.py
    4_SLA_Performance.py
.streamlit/
    config.toml
    secrets.example.toml
requirements.txt
README.md
```

You may use a different structure if it is cleaner.

---

# Acceptance Criteria

The redesign is complete when:

1. All 4 pages work.
2. Demo mode works without credentials.
3. Google Sheets mode still works.
4. Existing lead scoring data displays correctly.
5. Existing escalation data displays correctly.
6. KPI cards respond to filters.
7. Charts respond to filters.
8. Lead Operations table is searchable and filterable.
9. Lead detail view works.
10. Source drilldown works.
11. SLA queue works.
12. Empty datasets do not crash the app.
13. No secrets are exposed.
14. Dashboard looks significantly more professional than default Streamlit.
15. Overall visual quality should match or exceed the supplied dashboard reference image.

---

# Implementation Priority

Build in this order:

1. Shared data layer
2. Shared styling and components
3. Executive Overview
4. Lead Operations
5. Source Analytics
6. SLA & Performance
7. Demo-data expansion
8. Responsive polish
9. Error-state polish
10. README screenshots / documentation updates

---

# Important Constraint

Do not change or break the existing Make.com automations.

This task is a front-end and analytics redesign around the existing operational data.

---

# Final Deliverable

A polished, portfolio-ready Streamlit application that presents the dealership automation project as a credible sales-operations platform.

The final result should be suitable for:
- LinkedIn
- GitHub
- job applications
- interviews
- live portfolio demonstrations
