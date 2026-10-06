# Dealership Sales Automation & Analytics Platform

An end-to-end portfolio project that combines **workflow automation, lead scoring, SLA monitoring, Google Sheets, and an interactive Streamlit dashboard** for a simulated automotive dealership.

> **Portfolio disclaimer:** This project uses synthetic dealership and customer data. It was not deployed into a live dealership CRM.

![Dealership Sales Operations Dashboard](assets/dashboard-overview.png)

## Business Problem

Dealership leads arrive from multiple sources such as Website, Facebook, Google Ads, Carsales, referrals, and showroom walk-ins. Without a structured process, high-intent customers can be missed, response times can slip, and managers may have limited visibility into lead quality and follow-up performance.

## Solution

I built a connected sales-operations system that:

- captures structured dealership enquiries
- applies rule-based lead scoring
- classifies leads as **HOT, WARM, or NURTURE**
- assigns leads to Digital or Showroom sales teams
- generates a recommended next action
- stores operational data in Google Sheets
- monitors HOT leads against a **30-minute response SLA**
- automatically escalates missed HOT leads
- presents the data in an interactive Streamlit dashboard

## Architecture

```text
Lead Enquiry
    ↓
Make.com Lead Intake
    ↓
Scoring & Qualification
    ↓
Priority + Team Assignment
    ↓
Google Sheets Lead Database
    ↓
15-Minute SLA Monitor
    ↓
30-Minute HOT Lead Escalation
    ↓
Streamlit Sales Operations Dashboard
```

![System Architecture](assets/system-architecture.png)

## Tech Stack

| Tool | Purpose |
|---|---|
| Make.com | Workflow automation and business rules |
| Google Sheets | Operational lead data store |
| Python | Dashboard logic and data processing |
| Streamlit | Interactive dashboard |
| Pandas | Data transformation |
| Plotly | Interactive visualisations |
| Google Sheets API | Live dashboard data connection |

## Automation 1 — Lead Intake & Qualification

The intake workflow captures:

- Customer Name
- Email
- Phone
- Lead Source
- Vehicle of Interest
- Budget
- Purchase Timeline
- Trade-In
- Finance Required

It then automatically creates:

- Lead Score
- Priority
- Assigned Team
- Recommended Next Action
- Status

### Scoring Logic

The model considers purchase timeline, finance requirement, trade-in intent, budget, and lead source.

Example weighting:

| Factor | Example |
|---|---:|
| Purchase within 7 days | +40 |
| Purchase within 30 days | +30 |
| Finance required | +15 |
| Trade-in | +10 |
| Higher budget | Additional weighting |
| Referral source | Additional weighting |

### Priority Logic

- **HOT** → immediate sales attention
- **WARM** → same-day follow-up
- **NURTURE** → longer-term follow-up

Example recommended actions:

- HOT → `Call within 10 minutes and book test drive`
- WARM → `Call today and send vehicle options`
- NURTURE → `Add to nurture follow-up and check in within 7 days`

## Automation 2 — HOT Lead SLA Monitoring

A second Make.com scenario runs every **15 minutes** and checks for:

```text
Priority = HOT
Status = New
```

If a HOT lead remains untouched for more than **30 minutes**, the workflow updates:

- Status → `Escalation Required`
- Escalated At → timestamp
- Escalation Reason → audit note

This creates a simple, auditable response-SLA process.

## Google Sheets Data Model

The operational dataset records:

```text
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
```

## Interactive Dashboard

The Streamlit dashboard provides:

### KPI Cards

- Total Leads
- HOT Leads
- WARM Leads
- NURTURE Leads
- Escalations
- HOT Lead Rate

### Interactive Filters

- Lead Source
- Priority
- Status
- Assigned Team

### Visual Analytics

- Leads by Source
- Priority Mix
- Average Lead Score by Source
- Lead Activity Over Time

### Operational Alerts

- HOT + New
- Escalation Required
- Finance Required
- Trade-In Leads

### Lead Operations Table

A searchable operational table provides record-level visibility into customers, vehicles, scores, priorities, assignments, next actions, and escalation data.

## Business Value

This solution demonstrates how automation and analytics can support:

- faster response to high-intent leads
- consistent lead prioritisation
- fewer missed follow-ups
- stronger management visibility
- auditable SLA monitoring
- better source-performance analysis
- more structured sales operations

## Skills Demonstrated

**Business Analysis**
- process mapping
- business rule design
- workflow optimisation
- SLA definition
- operational requirements

**Data Analytics**
- KPI design
- lead segmentation
- dashboard development
- source-performance analysis
- operational reporting

**Automation & Development**
- Make.com scenario design
- conditional logic
- scheduled workflows
- Python
- Streamlit
- Pandas
- Plotly
- Google Sheets API

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app includes a **Demo data** mode so it can run without Google credentials.

## Connect Live Google Sheets Data

1. Create a Google Cloud project.
2. Enable the Google Sheets API and Google Drive API.
3. Create a service account.
4. Share the portfolio Google Sheet with the service-account email.
5. Copy `.streamlit/secrets.example.toml` to `.streamlit/secrets.toml`.
6. Replace the placeholders with your service-account values.
7. Run the dashboard and select **Google Sheets**.

> Never commit `.streamlit/secrets.toml` or private credentials to GitHub.

## Future Enhancements

- CRM integration
- email/SMS escalation alerts
- salesperson-level SLA reporting
- appointment and test-drive tracking
- sold/lost conversion tracking
- source-level conversion rates
- AI-generated follow-up messages
- predictive lead scoring
- automated aged-lead re-engagement

## Project Takeaway

This project demonstrates how **automation + operational data + analytics** can be combined into a complete sales-operations workflow rather than treated as separate tools.

---

Built as a portfolio project using simulated dealership data.
